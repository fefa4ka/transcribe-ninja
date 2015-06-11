angular.module( 'transcribe-ninja.main', [
  'ui.router'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'main', {
    url: '/',
    views: {
      "main": {
        controller: 'MainCtrl',
        templateUrl: 'main/main.tpl.html'
      }
    },
    data:{ pageTitle: 'Стенографирование разговоров' }
  });
}])

.controller( 'MainCtrl', ["$scope", "$translate", function MainCtrl( $scope, $translate) {
  $translate.use("ru");


}])

;
