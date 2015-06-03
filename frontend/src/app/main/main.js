angular.module( 'transcribe-ninja.main', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'main', {
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
.directive('mainLogo', function () {
  return {
    restrict: 'E',
    templateUrl: 'main/main.logo.tpl.html',
    link: function (scope, element, attrs) {
      console.log('make logo');
    }
  };
})
.controller( 'MainCtrl', function MainCtrl( $scope, $interval, $translate, $modal, $log, api ) {
  $translate.use("ru");


  $scope.upload = function() {
    console.log('upload');
  };



})

;
