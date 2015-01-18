$.fn.selectRange = function(start, end) {
    if(!end) end = start; 
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

angular.module( 'transcribe-ninja.record', [
  'transcribe-ninja.order',
  'ui.router',
  'cfp.hotkeys'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'work', {
    url: '/work',
    views: {
      "main": {
        controller: 'WorkCtrl',
        templateUrl: 'work/work.tpl.html'
      }
    },
    data:{ pageTitle: 'Ваши записи' }
  });
})


.controller( 'WorkCtrl', function RecordCtrl($scope, $translate, $modal, $stateParams, hotkeys, api) {
  function get_piece(piece_id) {

  }

  $translate.use("ru");

  $scope.wavesurfer = Object.create(WaveSurfer);

  $scope.wavesurfer.init({
      container: document.querySelector('#player'),
      waveColor: '#c1c1c1',
      cursorColor: '#337ab7',
      progressColor: '#337ab7',
      // height: 64,
      minPxPerSec: 40
      // scrollParent: true,
      // pixelRatio: 1
  });

  $scope.wavesurfer.on('play', function () {
      $('.fa-play')
          .removeClass('fa-play')
          .addClass('fa-pause');
  });

  $scope.wavesurfer.on('pause', function () {
      $('.fa-pause')
          .removeClass('fa-pause')
      .addClass('fa-play');
  });

  hotkeys.bindTo($scope).add({
      combo: 'esc',
      description: 'Play or pause',
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.playPause();
      }
  }).
  add({
      combo: 'alt+left',
      description: 'Backward',
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipBackward();
      }
  }).
  add({
      combo: 'alt+right',
      description: 'Forward',
      callback: function(event, hotkey) {
          event.preventDefault();
          $scope.wavesurfer.skipForward();
      }
  });

  $scope.loadQueue = function () {
    $scope.wavesurfer.clearRegions();
    
    $scope.queue = {};

    $scope.queue = api.queue.get({ }, function() {
      duration = 0;
      for(index in $scope.queue.pieces) {
        duration += $scope.queue.pieces[index].duration;
      }
      $scope.queue.duration = duration;

      $scope.wavesurfer.load($scope.queue.audio_file);
    });
  }

  hotkeys.bindTo($scope).add({
    combo: 'enter',
    description: 'Split',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target),
          text = $input.val()
          index = 0;
      
      event.preventDefault();

      // Если событие произошло не в инпуте иил инпут пустой
      if($input.is('textarea') == false || text == "") {
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

        $scope.$apply();

        // Перемещаем курсор
        $current_input = $('textarea[data-piece=' + piece.id + '][data-index=' + index + ']');
        $current_input.focus();
        $current_input[0].selectionStart = $current_input[0].selectionEnd = 0;

      } else {
        piece = $scope.queue.pieces[$scope.queue.pieces.length-1];
        index = (piece.transcriptions && piece.transcriptions.length) || 0;

        if($input[0].selectionStart == $input.val().length ) {
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

      $('textarea').autosize();
    }
  })
  .add({
    combo: 'backspace',
    description: 'Join',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target),
          text = $input.val(),
          index = $input.data('index');
      
      // Если событие произошло не в инпуте иил инпут пустой
      if($input.is('textarea') == false || index == 0 || typeof index == "undefined") {
        return;
      }

      if($input[0].selectionStart == 0) {
        event.preventDefault();

        // Ищем кусок с нужным айди
        for(index in $scope.queue.pieces) {
          piece = $scope.queue.pieces[index];
          if (piece.id == $input.data('piece')) {
            break;
          }
        }

        index = $input.data('index') - 1;
        // К предыдущей добавляем содержание текущией
        $previous_input = $('textarea[data-piece=' + piece.id + '][data-index=' + index  + ']');
        length = $previous_input.val().length;

        $previous_input.val( $previous_input.val() + $input.val() );

        $previous_input.focus();
        // $previous_input[0].selectionStart = $previous_input[0].selectionEnd = length;
        $previous_input.selectRange(length);

        // Удаляем текущую
        piece.transcriptions.splice(index + 1, 1);
      }

    }
  }).add({
    combo: 'down',
    description: 'Next',
    allowIn: ['TEXTAREA'],
    callback: function(event, hotkey) {
      var $input = $(event.target),
          text = $input.val(),
          index = $input.data('index');
      
      // Если событие произошло не в инпуте иил инпут пустой
      if($input.is('textarea') == false) {
        return;
      }

      // Ищем кусок с нужным айди
      for(index in $scope.queue.pieces) {
        piece = $scope.queue.pieces[index];
        if (piece.id == $input.data('piece')) {
          break;
        }
      }

      index = $input.data('index') + 1;
      
      // К предыдущей добавляем содержание текущией
      $next_input = $('textarea[data-piece=' + piece.id + '][data-index=' + index  + ']');
      
      if($next_input.length == 0) {
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
          index = $input.data('index');
      
      // Если событие произошло не в инпуте иил инпут пустой
      if($input.is('textarea') == false) {
        return;
      }

      // Ищем кусок с нужным айди
      for(index in $scope.queue.pieces) {
        piece = $scope.queue.pieces[index];

        if(index == 0) {
          previous_piece = piece;
        } else {
          previous_piece = $scope.queue.pieces[index-1];
        }

        if (piece.id == $input.data('piece')) {
          break;
        }
      }

      if($input.data('piece') > 0) {
        index = $input.data('index') - 1;
      } else {
        index = piece.transcriptions.length - 1;
      }
      
      // К предыдущей добавляем содержание текущией
      $next_input = $('textarea[data-piece=' + piece.id + '][data-index=' + index  + ']');
      
      if($next_input.length == 0) {
        $next_input = $('textarea[data-piece=' + previous_piece.id + '][data-index=' + previous_piece.transcriptions.length  + ']');
      }


      if($input[0].selectionStart == 0) {
        $next_input.focus();
        $next_input.selectRange($next_input.val().length);
      }
  }
});

 
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
         color: 'rgba(183,211,170,0.2)'
      });
      
  });

  //      * Random RGBA color.
  //      */
  //   $scope.transcription = api.transcription.list({ recordId: $stateParams.recordId }, function () {
  //     function randomColor(alpha) {
  //         return 'rgba(' + [
  //             ~~(Math.random() * 255),
  //             ~~(Math.random() * 255),
  //             ~~(Math.random() * 255),
  //             alpha || 1
  //         ] + ')';

  //     }

  //     var colors = {};
      
  //     for(var i in $scope.transcription) {
  //         var transcription = $scope.transcription[i];

  //         if(typeof colors[transcription.speaker] == "undefined") {
  //             colors[transcription.speaker] = randomColor(0.1);
  //         }
          
  //         $scope.wavesurfer.addRegion({ 
  //             start: transcription.start_at,
  //             end: transcription.end_at,
  //             color: colors[transcription.speaker]
  //         });
          

  //     }
  //   });

  $scope.$on('$destroy', function iVeBeenDismissed() {
    $scope.wavesurfer.destroy();
  });

  $scope.loadQueue();
  $('textarea').autosize();
})

;
