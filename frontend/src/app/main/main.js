angular.module( 'transcribe-ninja.main', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'main-page', {
    url: '/',
    views: {
      "main": {
        controller: 'MainCtrl',
        templateUrl: 'main/main.tpl.html'
      }
    },
    data:{ pageTitle: 'Transcribe.ninja – стенографирование разговоров' }
  });
})

.controller( 'MainCtrl', function MainCtrl( $scope, $translate, $modal, $log, api ) {
  $translate.use("ru");

  $scope.upload = function() {
    console.log('upload');
  };



})

;
