angular.module( 'transcribe-ninja', [
  'templates-app',
  'templates-common',

  'transcribe-ninja.localization',
  'transcribe-ninja.api',
  'transcribe-ninja.auth',
  'transcribe-ninja.main',
  'transcribe-ninja.record',
  'transcribe-ninja.record.list',
  'transcribe-ninja.record.upload',
  'transcribe-ninja.work',

  'ui.router',
  'ui.bootstrap',
  'pascalprecht.translate',

  'ngResource'
])

.factory('Data', function() {
  return {
    user: ""
  };
})

.config( function myAppConfig ( $stateProvider, $urlRouterProvider ) {
  $urlRouterProvider.otherwise( '/' );

})

.config(['$httpProvider', function($httpProvider){
  // django and angular both support csrf tokens. This tells
  // angular which cookie to add to what header.
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])



.run( function run () {
})

.controller( 'AppCtrl', function AppCtrl ( $scope, $location, $translate, $modal, Data, api ) {
  $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
    if ( angular.isDefined( toState.data.pageTitle ) ) {
      $scope.pageTitle = toState.data.pageTitle + ' | Стенограф' ;
    }
  });

  $translate.use("ru");

  $scope.Data = Data;
  $scope.Data.user = api.account.get();


  $scope.logout = function(){
    api.auth.logout(function(){
      $scope.Data.user = undefined;
    });
  };
  
})

;

