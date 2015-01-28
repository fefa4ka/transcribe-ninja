angular.module( 'transcribe-ninja.record', [
  'transcribe-ninja.order',
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

.controller( 'RecordCtrl', function RecordCtrl($scope, $translate, $modal, $stateParams, hotkeys, api) {
  $translate.use("ru");

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

  $scope.wavesurfer.on('ready', function() {

    var pallete = ['rgba(251, 121, 123, 0.1)', 'rgba(219, 246, 120, 0.1)', 'rgba(94, 223, 214, 0.1)', 'rgba(184, 149, 181, 0.1)', 'rgba(94, 111, 125, 0.1)'],
        colors = {};

    for(var i in $scope.record.transcriptions) {
        var transcription = $scope.record.transcriptions[i];

        if(typeof colors[transcription.name] == "undefined") {
            colors[transcription.name] = pallete.pop();
        }
        
        console.log({ 
            start: transcription.start_at,
            end: transcription.end_at,
            color: colors[transcription.name],
            drag: false,
            resize: false
        });
        $scope.wavesurfer.addRegion({ 
            start: transcription.start_at,
            end: transcription.end_at,
            color: colors[transcription.name],
            drag: false,
            resize: false
        });
    }

  });
  
  $scope.$on('$viewContentLoaded', function() {
    $scope.resize_transcription_layout();
  });

  $scope.$on('$destroy', function iVeBeenDismissed() {
    $scope.wavesurfer.destroy();
  });


  

  $scope.record = api.record.get({ recordId: $stateParams.recordId }, function() {
    $scope.wavesurfer.load($scope.record.audio_file);
  });

  $scope.resize_transcription_layout = function () {
    var $element = $('.record_transcriptions'),
        vpw = $(window).width(),
        vph = $(window).height(),
        height = vph - $element.offset().top;

    $('.record_transcriptions').css({'height': height + 'px'});
  }

  $scope.order = function (record) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'order/order.modal.tpl.html',
      controller: 'OrderModalCtrl',
      windowClass: 'order-bill',
      resolve: {
        record: function () {
          return record;
        }
      }
    });
  };
  
  

});
