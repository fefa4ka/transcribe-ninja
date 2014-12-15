angular.module( 'transcribe-ninja.record', [
  'ui.router',
  'cfp.hotkeys'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'record', {
    url: '/record/{recordId:int}',
    views: {
      "main": {
        controller: 'RecordCtrl',
        templateUrl: 'record/record.tpl.html'
      }
    },
    data:{ pageTitle: 'Ваши записи' }
  });
})

.controller( 'RecordCtrl', function RecordCtrl($scope, $translate, $stateParams, hotkeys, api) {
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

  $scope.record = api.record.get({ recordId: $stateParams.recordId }, function() {
      $scope.wavesurfer.load('/media/record/' + $scope.record.url);
  });

  
  $scope.wavesurfer.on('ready', function() {/**
       * Random RGBA color.
       */
    $scope.transcription = api.transcription.list({ recordId: $stateParams.recordId }, function () {
      function randomColor(alpha) {
          return 'rgba(' + [
              ~~(Math.random() * 255),
              ~~(Math.random() * 255),
              ~~(Math.random() * 255),
              alpha || 1
          ] + ')';

      }

      var colors = {};
      
      for(var i in $scope.transcription) {
          var transcription = $scope.transcription[i];

          if(typeof colors[transcription.speaker] == "undefined") {
              colors[transcription.speaker] = randomColor(0.1);
          }
          
          $scope.wavesurfer.addRegion({ 
              start: transcription.start_at,
              end: transcription.end_at,
              color: colors[transcription.speaker]
          });
          

      }
    });
  
  });

  $scope.$on('$destroy', function iVeBeenDismissed() {
    $scope.wavesurfer.destroy();
  });
})

;
