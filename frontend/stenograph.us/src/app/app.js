angular.module( 'transcribe-ninja', [
  'templates-app',
  'templates-common',

  'transcribe-ninja.localization',
  'transcribe-ninja.api',
  'transcribe-ninja.auth',
  'transcribe-ninja.main',
  'transcribe-ninja.about',
  'transcribe-ninja.record',
  'transcribe-ninja.record.list',
  'transcribe-ninja.record.upload',

  'ui.router',
  'ui.bootstrap',
  'pascalprecht.translate',

  'ngResource'
])

.config(function($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
})

.config( ["$stateProvider", "$urlRouterProvider", function myAppConfig ( $stateProvider, $urlRouterProvider ) {
  $urlRouterProvider.otherwise( '/' );

}])

.config(['$httpProvider', function($httpProvider){
  // django and angular both support csrf tokens. This tells
  // angular which cookie to add to what header.
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])

.filter('secondsToDateTime', function() {
    return function(seconds) {
        var d = new Date(0,0,0,0,0,0,0);
        d.setSeconds(seconds);
        return d;
    };
})

.run( function run () {
})

.controller( 'AppCtrl', ["$scope", "$location", "$rootScope", "$state", "$translate", "$modal", "$interval", "$http", "api", function AppCtrl ( $scope, $location, $rootScope, $state, $translate, $modal, $interval, $http, api ) {
  $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
    if ( angular.isDefined( toState.data.pageTitle ) ) {
      $scope.pageTitle = toState.data.pageTitle + ' | Стенограф.ус' ;
      $scope.stateName = toState.name;      
    }
  });

  $scope.$on('$stateChangeStart', function (event, toState, toParams) {
    var requireLogin = toState.data.requireLogin;

    if (requireLogin && angular.isUndefined($rootScope.currentUser)) {
      event.preventDefault();
      // Мог ещё не подгрузится логин
      $http.get('/api/auth/me/').
        success(function(data, status, headers, config) {
          $rootScope.currentUser = data;
            $state.go(toState.name, toParams);
            
        }).
        error(function(data, status, headers, config) {
            $scope.authModal(function () {
              return $state.go(toState.name, toParams);
            });
        });
    }
  });

  $translate.use("ru");

  api.account.get().
    $promise.
    then(function (data) {
      if(angular.isUndefined(data.id)) {
        $rootScope.currentUser = undefined;
      } else {
        $rootScope.currentUser = data;
      }
    });

  $scope.authModal = function (authCallback) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'auth/auth.login.modal.tpl.html',
      controller: 'AuthModalCtrl',
      windowClass: 'auth-modal',
      resolve: {
        authCallback: function () {
          return authCallback;
        }
      }
    });
  };


  $scope.logout = function(){
    api.auth.logout(function(){
      $rootScope.currentUser = undefined;

      $location.path( "/" );
    });
  };

  
}])

;

