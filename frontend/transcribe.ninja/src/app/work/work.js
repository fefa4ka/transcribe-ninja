$.fn.selectRange = function(start, end) {
    if(!end) {
      end = start; 
    }
    return this.each(function() {
        if (this.setSelectionRange) {
            this.focus();
            this.setSelectionRange(start, end);
        } else if (this.createTextRange) {
            var range = this.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', start);
            range.select();
        }
    });
};

angular.module( 'transcribe-ninja.work', [
  'transcribe-ninja.player',

  'ngSanitize',
  'ui.router',
  'monospaced.elastic',
  'cfp.hotkeys'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'work', {
    url: '/work',
    views: {
      "main": {
        controller: 'WorkCtrl',
        templateUrl: 'work/work.tpl.html'
      }
    },
    data: { 
      pageTitle: 'Ваши записи',
      requireLogin: true
    }
  });
}])

.directive('autoFocus', ["$timeout", function($timeout) {
    return {
        restrict: 'AC',
        link: function(_scope, _element) {
            $timeout(function(){
                _element[0].focus();
            }, 0);
        }
    };
}])

.controller( 'WorkCtrl', ["$scope", "$rootScope", "$translate", "$modal", "$stateParams", "hotkeys", "api", "$interval", "$timeout", function WorkCtrl($scope, $rootScope, $translate, $modal, $stateParams, hotkeys, api, $interval, $timeout) {
  function get_piece(piece_id) {

  }

  $translate.use("ru");

  $scope.suggests_main = $scope.suggests = [
    'Каждую мысль и речь другого собеседника лучше начинать с новой строки', 
    'Если в записи несколько собеседников, выберете нужного человечка слева от текста', 
    'В разделе «<a href="#/history">История</a>» вся информация о вашей работе',
    '<a href="mailto:info@transcribe.ninja">Пишите нам</a> с любыми вопросами и предложениями',
    'Если вам что-то непонятно, <a href="mailto:info@transcribe.ninja">пишите нам</a>',
    'Пользуйтесь горячими клавишами для работы с записью',
    'Можно нажать <kbd>Esc</kbd>, чтобы приостановить воспроизведение записи',
    'Перематывайте запись с помощью стрелок на клавиатуре',
    'Отличный <a href="http://therules.ru" target="blank">сайт с правилами русского языка</a><br/><small><a href="http://therules.ru" target="blank">therules.ru</a></small>',
    'Иногда перед полем ввода транскрибции есть текст — это часть предыдущего куска.<br/>Так вы можете понять с какого момента распознавать.',
    'Не печатать эканья, аканья и слова паразиты'
  ];

  $scope.suggests_transcribe = [
    'Помечайте, если речь в записи неразборчивая',
    'Удобно послушать пару слов, нажать паузу и напечатать их'
  ];

  $scope.suggests_check = [
    'Соединяйте разорванные предложения',
    'Текст распознаёт робот, поэтому там может оказаться бред, просто сотрите и напечатайте правильно',
    'Расставляйте знаки препинания'
  ];

  // $scope.suggestStippet = function() {
  //   console.log('suggest',$scope.suggest);
  //  return $sce.trustAsHtml($scope.suggest);
  // };

  // Hotkeys
  // Player
  hotkeys.bindTo($scope).add({
      combo: 'esc',
      description: 'Play or pause',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.playPause();

          // Ya.Metrica 
          yaCounter27735045.reachGoal('keyboard_esc_play');
      }
  }).
  add({
      combo: 'alt+left',
      description: 'Backward',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipBackward();

          // Ya.Metrica 
          yaCounter27735045.reachGoal('keyboard_arrow_left');
      }
  }).
  add({
      combo: 'alt+right',
      description: 'Forward',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipForward();

          // Ya.Metrica 
          yaCounter27735045.reachGoal('keyboard_arrow_right');
      }
  }).

  // Editor
  add({
    combo: 'enter',
    description: 'Split',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target);
      
      event.preventDefault();

      $scope.applyTranscriptionChange($input, true);

      // Ya.Metrica 
      yaCounter27735045.reachGoal('new_line');
    }
  }).
  add({
    combo: 'ctrl+enter',
    description: 'Split',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      event.preventDefault();

      $scope.saveTranscription();

      // Ya.Metrica 
      yaCounter27735045.reachGoal('keyboard_save');
    }
  })
  .add({
    combo: 'backspace',
    description: 'Join',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target),
          text = $input.val(),
          input_index = $input.data('index'),
          piece,
          piece_id,
          previous_piece;
      
      // Больной разум всё это придумал, нужно документировать. 
      // Какая-то магия, почему это работает?
      // Если событие произошло не в инпуте иил инпут пустой
      if($input.is('textarea') === false || typeof input_index == "undefined") {
        return;
      }

      if($input[0].selectionStart === 0 && $input[0].selectionEnd === 0) {
        event.preventDefault();

        // Ищем кусок с нужным айди
        for(var index in $scope.queue.pieces) {
          piece = $scope.queue.pieces[index];
          piece_id = piece.id;
          
          if(index === 0 ) {
            previous_piece = piece;
          }
          if (piece.id == $input.data('piece')) {
            break;
          }

          previous_piece = piece;
          
        }

        if(input_index === 0 && piece != previous_piece) {
          piece_id = previous_piece.id;
          previous_input_index = previous_piece.transcriptions.length - 1;
        } else {

          previous_input_index = input_index - 1;
        }

        // TODO: убрать джиквери
        // Сделать копирование меньшей части в большую 


        // К предыдущей добавляем содержание текущией
        $previous_input = $('textarea[data-piece=' + piece_id + '][data-index=' + (previous_input_index)  + ']');
        var previous_length = $previous_input.val().length;
        var current_length = $input.val().length;
        
        if(current_length > previous_length) {
          // Если это на стыке кусков, удаляем крайний
          if(input_index > 0) {
            console.log('c > p same piece', input_index);

            previous_input_index = input_index - 1;

            piece.transcriptions[input_index].text = piece.transcriptions[previous_input_index].text + $input.val();
            piece.transcriptions.splice(input_index - 1, 1);

            console.log('c > p update', piece.transcriptions, $scope.queue.pieces);
          } else {
            previous_input_index = input_index;
            previous_length = previous_piece.transcriptions[previous_input_index].text.length;

            piece.transcriptions[input_index].text = previous_piece.transcriptions[previous_input_index].text + $input.val();

            console.log('c > p not same', previous_piece.transcriptions);
            previous_piece.transcriptions.pop();
          }

          piece_input_id = piece.id;
          

          // Удаляем другой
        } else {

          // $previous_input.val( $previous_input.val() + $input.val() );
          // $previous_input.trigger('input');

          if(input_index > 0) {
            console.log('same piece', input_index);

            piece_input_id = piece.id;

            piece.transcriptions[previous_input_index].text += piece.transcriptions[input_index].text;
            
          } else {
            console.log('not same piece');

            previous_input_index = previous_piece.transcriptions.length - 1;
            piece_input_id = previous_piece.id;

            previous_piece.transcriptions[previous_input_index].text += piece.transcriptions[input_index].text;
            
          }

          
          // Если это на стыке кусков, удаляем крайний
          console.log('c < p', piece.transcriptions, input_index);
          piece.transcriptions.splice(input_index, 1);
          console.log('c < p update', piece.transcriptions, $scope.queue.pieces);

        }

        setTimeout(function(){ 
          console.log(piece_input_id, previous_input_index);
          $previous_input = $('textarea[data-piece=' + piece_input_id + '][data-index=' + (previous_input_index)  + ']');
          $previous_input.focus();
          // $previous_input[0].selectionStart = $previous_input[0].selectionEnd = length;
          $previous_input.selectRange(previous_length);
        });

        // Ya.Metrica 
        yaCounter27735045.reachGoal('join_lines');
      }

    }
  }).
  // Navigation
  add({
    combo: 'down',
    description: 'Next',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target),
          text = $input.val(),
          piece = {},
          input_index = $input.data('index');
      
      // Если событие произошло не в инпуте иил инпут пустой
      // Если мы в последнем поле, то ничего не делаем
      if($input.is('textarea') === false || typeof $input.data('piece') == "undefined") {
        return;
      }

      // Ищем кусок с нужным айди
      for(var index in $scope.queue.pieces) {
        next_piece = $scope.queue.pieces[index];

        if (piece.id == $input.data('piece')) {
          break;
        }

        piece = next_piece;
      }


      if(input_index == piece.transcriptions.length - 1 && piece != next_piece) {
        piece = next_piece;
        input_index = 0;

      } else {
        input_index += 1;
      }
      
      // К предыдущей добавляем содержание текущией
      $next_input = $('textarea[data-piece=' + piece.id + '][data-index=' + input_index  + ']');
      
      if($next_input.length === 0) {
        $next_input = $('#new-transcription');
      }

      if($input[0].selectionStart == $input.val().length) {
        $next_input.focus();
        $next_input.selectRange(0);
      }

      // Ya.Metrica 
      yaCounter27735045.reachGoal('keyboard_arrow_down');
    }
  }).add({
      combo: 'up',
      description: 'Previous',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
        var $input = $(event.target),
            text = $input.val(),
            input_index = $input.data('index');
        
        // Если событие произошло не в инпуте
        if($input.is('textarea') === false || ($input.data('piece') == $scope.queue.pieces[0].id && input_index === 0)) {
          return;
        }

        // Ищем кусок с нужным айди
        for(var index in $scope.queue.pieces) {
          piece = $scope.queue.pieces[index];

          if (piece.id == $input.data('piece')) {
            break;
          }

          previous_piece = piece;
        }

        if($input.data('piece') > 0) {
          input_index = $input.data('index') - 1;
        } else {
          input_index = piece.transcriptions.length - 1;
        }
        
        // К предыдущей добавляем содержание текущией
        $next_input = $('textarea[data-piece=' + piece.id + '][data-index=' + input_index  + ']');
        
        if($next_input.length === 0) {
          $next_input = $('textarea[data-piece=' + previous_piece.id + '][data-index=' + (previous_piece.transcriptions.length - 1)  + ']');
        }


        if($input[0].selectionStart === 0) {
          $next_input.focus();
          $next_input.selectRange($next_input.val().length);
        }

        // Ya.Metrica 
        yaCounter27735045.reachGoal('keyboard_arrow_up');
    }
  });

  // // Player
  // $scope.wavesurfer = Object.create(WaveSurfer);

  // $scope.wavesurfer.init({
  //     container: document.querySelector('.player'),
  //     waveColor: '#c1c1c1',
  //     cursorColor: '#337ab7',
  //     progressColor: '#337ab7',
  //     // height: 64,
  //     minPxPerSec: 40
  //     // scrollParent: true,
  //     // pixelRatio: 1
  // });

  // $scope.wavesurfer.on('play', function () {
  //     $('.fa-play')
  //         .removeClass('fa-play')
  //         .addClass('fa-pause');
  // });

  // $scope.wavesurfer.on('pause', function () {
  //     $('.fa-pause')
  //         .removeClass('fa-pause')
  //     .addClass('fa-play');
  // });
  
  $scope.playerInit = function () {
    $scope.wavesurfer.on('ready', function() {
        // Выделяем кусок, который нужно распознать

        // Если начало куска, раньше чем через 1.5 сек, то распознаем раньше
        // start_at = 1.5;

        // if($scope.queue.pieces[0].start_at < start_at) {
        //   start_at = 0;
        // } 
        
        // end_at = start_at + $scope.queue.duration;

        // $scope.wavesurfer.addRegion({ 
        //    start: start_at,
        //    end: end_at,
        //    color: 'rgba(183,211,170,0.4)',
        //    drag: false,
        //    resize: false
        // });

        // $scope.wavesurfer.play();
        // $scope.wavesurfer.pause();
        
    });

    
  };

  $scope.$on('$destroy', function iVeBeenDismissed() {
    $scope.wavesurfer.destroy();
  });

  $scope.textareaAdjust = function () {
    // Выравниваем текстареа. Костыль BUG
    window.dispatchEvent(new Event('resize'));
    $rootScope.$broadcast('elastic:adjust');
  };

  $scope.selectSpeaker = function (transcription, index, same_gender) {
    // Прячем выбор сразу
    transcription.speakerHover = false;

    if(same_gender === false) {
      if(transcription.gender == "F") {
        transcription.gender = "M";
      } else {
        transcription.gender = "F";
      }
    } 

    transcription.speaker_code = transcription.gender + index;

    // Ya.Metrica 
    yaCounter27735045.reachGoal('speaker_selection');
  };
  
  $scope.newTranscription = {};

  // Загрузка задачи
  $scope.loadQueue = function (skip) {  
    $scope.queue = {};
    $scope.originalTranscriptions = [];

    // Считаем в метрику
    if(skip === true) {
      yaCounter27735045.reachGoal('skip');
    }

    $('#new-transcription').val("");
    
    api.account.get().
      $promise.
        then(function (data) {
          $rootScope.currentUser = data;
        });
        
    // Загружаем 
    api.queue.get().
      $promise.
      then(function(data) {
        $scope.queue = data;
        // Считаем продолжительность общую
        duration = 0;
        for(var index in $scope.queue.pieces) {
          duration += $scope.queue.pieces[index].duration;
        }

        $scope.queue.duration = duration;

        // Подгружаем аудиофайл 
        $scope.wavesurfer.clearRegions();
        $scope.wavesurfer.load($scope.queue.audio_file);

        // Оригинальная транскрипция
        for(var p_index in $scope.queue.pieces) {
          var piece = $scope.queue.pieces[p_index];
          for(var t_index in piece.transcriptions) {
            $scope.originalTranscriptions.push(piece.transcriptions[t_index].text);
          }
        }

        $scope.newTranscription = {
          gender: $scope.queue.pieces[0].speaker,
          speaker_code: $scope.queue.pieces[0].speaker + '1'
        };

        // Обновляем советы
        
        if($scope.queue.work_type === 0) {
          $scope.suggests = $scope.suggests_main.concat($scope.suggests_transcribe);
        } else {
          $scope.suggests = $scope.suggests_main.concat($scope.suggests_check);
        }

        $scope.suggest = $scope.suggests[Math.floor(Math.random() * $scope.suggests.length)];
        // TODO: Избавиться от таймаута. Нужен, потому что ресайз делается после рендера
        $timeout($scope.textareaAdjust, 500);
        // Выравниваем текстареа. Костыль BUG
        // window.dispatchEvent(new Event('resize'));
        // $rootScope.$broadcast('elastic:adjust');
    });
  };

  // Сохранение транскрипции
  $scope.saveTranscription = function () {
    var transcriptions = [];

    // Добавляем в модель данные из формы
    $scope.applyTranscriptionChange($('#new-transcription'));

    $scope.queue.saving = true;

    // Готовим данные
    for(var p_index in $scope.queue.pieces) {
      var piece = $scope.queue.pieces[p_index];

      for (var t_index in piece.transcriptions) {
        var transcription = piece.transcriptions[t_index];

        transcriptions.push({
          queue: $scope.queue.id,
          piece: piece.id,
          text: transcription.text,
          index: t_index,
          speaker_code: transcription.speaker_code
        });
      }
    }
    
    // Отравляем данные на сервер
    api.transcription.create(transcriptions, function () {
      // Загружаем новую задачу
      $scope.loadQueue();
    }, function () {
      $scope.loadQueue();
      yaCounter27735045.reachGoal('transcription_save_error');

    });

    // Ya.Metrica
    if($scope.queue.work_type == 0) {
      yaCounter27735045.reachGoal('transcribe');
    } else {
      yaCounter27735045.reachGoal('check_transcribe');
    }
  };

  $scope.poorRecord = function () {
    // Отравляем данные на сервер
    api.transcription.create({
        queue: $scope.queue.id,
        poor: 1
      },  
      function () {
        // Загружаем новую задачу.
        // Сервер вернёт
        $scope.loadQueue();
    });

    yaCounter27735045.reachGoal('poor_queue');
  };

  $scope.workLength = function () {
    var length = 0,
        check_length = 0,
        original_transcriptions = [],
        transcriptions = [];

    if($scope.queue) {
      $('textarea.transcriptions').each(function(index) { 
        if($(this).val().length > 0) {
          transcriptions.push($(this).val());

          length += $(this).val().length; 
        }
      });

      if($scope.queue.work_type === 0) {
        return length;

      } else {
        // Смотрим измненеия
        var dmp = new diff_match_patch();

        var diffs = dmp.diff_main($scope.originalTranscriptions.join("\n"), transcriptions.join("\n"));
        // Семантически. Дорого
        dmp.diff_cleanupSemantic(diffs);

        for(var index in diffs) {
          var diff = diffs[index];
          // Если была работа 1 — добавление -1 - удаление
          if([1].indexOf(diff[0]) > -1) {
            // console.log(diff[1]);
            check_length += diff[1].length;
          }
        }

        return check_length;
      }
    }
  };
  // Подсчёт заработанного бабла
  $scope.earnMoneyValue = function () {  
    if($scope.queue) {
      if($scope.queue.work_type === 0) {
        return $scope.workLength() * $scope.queue.price;
      } else {
        return $scope.queue.total_price + $scope.workLength() * $scope.queue.price;
      }
    }
  };



  // Добавить данные в модель
  $scope.applyTranscriptionChange = function ($input, enter) {
    var text = $input.val(),
        transcription = $scope.newTranscription,
        index = 0;
    
    console.log($scope.queue.pieces, $input, $input.val(), $input.data('index'));

    // Если событие произошло не в инпуте иил инпут пустой
    if($input.is('textarea') === false || $input.val() === "") {
      return;
    }

    // Если курсор в самом начале, и предыдущая пустая, то ничего не делаем

    // Если разделяем существующую транскрипцию
    if(typeof $input.data('index') != "undefined" && typeof enter !== "undefined") {
      // Ищем кусок с нужным айди
      for(index in $scope.queue.pieces) {
        piece = $scope.queue.pieces[index];
        if (piece.id == $input.data('piece')) {
          break;
        }
      }

      index = $input.data('index') + 2;

      // Часть, которая остаётся
      piece.transcriptions[$input.data('index')].text = text.slice(0, $input[0].selectionStart);
      // $input.val(text.slice(0, $input[0].selectionStart));
      // $input.trigger('input');

      var speaker_code = piece.transcriptions[$input.data('index')].speaker_code,
          gender = piece.transcriptions[$input.data('index')].gender;

      // Добавляем в нужное место
      piece.transcriptions.splice(index, 0, {
        piece: piece.id,
        text: text.slice($input[0].selectionStart, text.length).trim(),
        speaker_code: speaker_code,
        gender: gender
      });

      // После того как отрендерица переводим курсор
      setTimeout(function(){ 
        // Перемещаем курсор
        var current_index = $input.data('index') + 1;
        $current_input = $('textarea[data-piece=' + piece.id + '][data-index=' + current_index + ']');
        console.log(index, piece.id, $current_input[0]);
        $current_input.focus();
        $current_input[0].selectionStart = $current_input[0].selectionEnd = 0;
      });

    } else {
      piece = $scope.queue.pieces[$scope.queue.pieces.length-1];
      index = (piece.transcriptions && piece.transcriptions.length) || 0;

      if($input[0].selectionStart == $input.val().length || $input[0].selectionStart === 0 || typeof enter === "undefined") {
        piece.transcriptions.push({
          piece: piece.id,
          text: transcription.text,
          speaker_code: transcription.speaker_code,
          gender: transcription.gender
        });
      } else {
        piece.transcriptions.push({
          piece: piece.id,
          text: transcription.text.slice(0, $input[0].selectionStart),
          speaker_code: transcription.speaker_code,
          gender: transcription.gender
        });

        piece.transcriptions.push({
          piece: piece.id,
          text: transcription.text.slice($input[0].selectionStart, text.length),
          speaker_code: transcription.speaker_code,
          gender: transcription.gender
        });
      }

      // Чистим форму
      $input.val("");

      
    }
  };

  $scope.loadQueue();

}])

;
