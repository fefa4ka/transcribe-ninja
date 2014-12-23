angular.module( 'transcribe-ninja.player', [
  'ui.router'
])

.directive('tnPlayer', function () { 
  return {
    restrict: 'E',
    templateUrl: 'player/player.tpl.html',

    link: function (scope, element, attrs) {
        var player = element.children()[0],
            file_path = attrs['src'];

        scope.wavesurfer = Object.create(WaveSurfer);
        scope.loading_percent =0;
        
        scope.wavesurfer.init({
          container: player,
          waveColor: '#c1c1c1',
          cursorColor: '#337ab7',
          progressColor: '#337ab7',
          minPxPerSec: 40
          // scrollParent: true,
          // pixelRatio: 1
        });

        scope.wavesurfer.on('play', function () {
            $('.fa-play')
              .removeClass('fa-play')
              .addClass('fa-pause');
        });

        scope.wavesurfer.on('pause', function () {
          $('.fa-pause')
              .removeClass('fa-pause')
          .addClass('fa-play');
        });

        scope.wavesurfer.on('loading', function (percent) {
            scope.loading_percent = percent;
            scope.$apply();
        });

        scope.wavesurfer.load(file_path);


        scope.duration = scope.wavesurfer.getDuration();
    }
  };
})

;

