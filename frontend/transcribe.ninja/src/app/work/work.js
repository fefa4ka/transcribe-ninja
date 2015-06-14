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

  // Обноваляем баланс часто
  $interval(function () {
      api.account.get().
        $promise.
          then(function (data) {
            $rootScope.currentUser = data;
          });
    }, 5000);

  $translate.use("ru");

  // Hotkeys
  // Player
  hotkeys.bindTo($scope).add({
      combo: 'esc',
      description: 'Play or pause',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.playPause();
      }
  }).
  add({
      combo: 'alt+left',
      description: 'Backward',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipBackward();
      }
  }).
  add({
      combo: 'alt+right',
      description: 'Forward',
      allowIn: ['TEXTAREA'],
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipForward();
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

      $scope.applyTranscriptionChange($input);
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
          
          if(index == 0 ) {
            previous_piece = piece;
          }
          console.log(index, piece, previous_piece, piece_id);
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
          $input.val( $previous_input.val() + $input.val() );

          $input.selectRange(previous_length);
          console.log('pieces', piece, previous_piece);
          // Если это на стыке кусков, удаляем крайний
          if(piece == previous_piece || input_index > 0) {
            console.log('c > p same piece', previous_piece.transcriptions);

            piece.transcriptions.splice(input_index - 1, 1);
            console.log('c > p update', piece.transcriptions, $scope.queue.pieces);
          } else {
            console.log('c > p not same', previous_piece.transcriptions);
            previous_piece.transcriptions.pop();
          }
          // Удаляем другой
        } else {

          $previous_input.val( $previous_input.val() + $input.val() );

          $previous_input.focus();
          // $previous_input[0].selectionStart = $previous_input[0].selectionEnd = length;
          $previous_input.selectRange(previous_length);

          // Если это на стыке кусков, удаляем крайний
          console.log('c < p', piece.transcriptions, input_index);
          piece.transcriptions.splice(input_index, 1);
          console.log('c < p update', piece.transcriptions, $scope.queue.pieces);
        }

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
        start_at = 1.5;

        if($scope.queue.pieces[0].start_at < start_at) {
          start_at = 0;
        } 
        
        end_at = start_at + $scope.queue.duration;

        $scope.wavesurfer.addRegion({ 
           start: start_at,
           end: end_at,
           color: 'rgba(183,211,170,0.2)',
           drag: false,
           resize: false
        });
        
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

  // Загрузка задачи
  $scope.loadQueue = function () {  
    $scope.queue = {};
    $scope.originalTranscriptions = [];

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

    // Готовим данные
    for(var p_index in $scope.queue.pieces) {
      var piece = $scope.queue.pieces[p_index];

      for (var t_index in piece.transcriptions) {
        var transcription = piece.transcriptions[t_index];

        transcriptions.push({
          queue: $scope.queue.id,
          piece: piece.id,
          text: transcription.text,
          index: t_index
        });
      }
    }

    // Отравляем данные на сервер
    api.transcription.create(transcriptions, function () {
      // Загружаем новую задачу
      $scope.loadQueue();
    });
  };

  // Подсчёт заработанного бабла
  $scope.earnMoneyValue = function () {
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
        return length * $scope.queue.price;
      } else {
        // Смотрим измненеия
        var dmp = new diff_match_patch();

        var diffs = dmp.diff_main($scope.originalTranscriptions.join("\n"), transcriptions.join("\n"));
        for(var index in diffs) {
          var diff = diffs[index];
          // Если была работа 1 — добавление -1 - удаление

          if([1,-1].indexOf(diff[0]) > -1) {
            // console.log(diff[1]);
            check_length += diff[1].length;
          }
        }

        return $scope.queue.total_price + check_length * $scope.queue.price;
      }
    }
  };

  // Добавить данные в модель
  $scope.applyTranscriptionChange = function ($input) {
    var text = $input.val(),
        index = 0;
  

    // Если событие произошло не в инпуте иил инпут пустой
    if($input.is('textarea') === false || $input.val() === "") {
      return;
    }

    // Если курсор в самом начале, и предыдущая пустая, то ничего не делаем

    // Если разделяем существующую транскрипцию
    if(typeof $input.data('index') != "undefined") {
      // Ищем кусок с нужным айди
      for(index in $scope.queue.pieces) {
        piece = $scope.queue.pieces[index];
        if (piece.id == $input.data('piece')) {
          break;
        }
      }

      index = $input.data('index') + 1;

      // Часть, которая остаётся
      $input.val(text.slice(0, $input[0].selectionStart));

      // Добавляем в нужное место
      piece.transcriptions.splice(index, 0, {
        piece: piece.id,
        text: text.slice($input[0].selectionStart, text.length).trim()
      });

      // После того как отрендерица переводим курсор
      setTimeout(function(){ 
        // Перемещаем курсор
        $current_input = $('textarea[data-piece=' + piece.id + '][data-index=' + index + ']');

        $current_input.focus();
        $current_input[0].selectionStart = $current_input[0].selectionEnd = 0;
      });

    } else {
      piece = $scope.queue.pieces[$scope.queue.pieces.length-1];
      index = (piece.transcriptions && piece.transcriptions.length) || 0;

      if($input[0].selectionStart == $input.val().length || $input[0].selectionStart === 0) {
        piece.transcriptions.push({
          piece: piece.id,
          text: text
        });
      } else {
        piece.transcriptions.push({
          piece: piece.id,
          text: text.slice(0, $input[0].selectionStart)
        });

        piece.transcriptions.push({
          piece: piece.id,
          text: text.slice($input[0].selectionStart, text.length)
        });
      }

      // Чистим форму
      $input.val("");
    }

  };

  $scope.loadQueue();

}])

;
