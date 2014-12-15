angular.module( 'transcribe-ninja', [
  'templates-app',
  'templates-common',

  'transcribe-ninja.auth',
  'transcribe-ninja.record',
  'transcribe-ninja.record.list',
  'transcribe-ninja.record.upload',

  'ui.router',
  'ui.bootstrap',
  'pascalprecht.translate',
  'humanSeconds',

  'ngResource'
])

.factory('Data', function() {
  return {
    user: ""
  };
})

.config( function myAppConfig ( $stateProvider, $urlRouterProvider ) {
  $urlRouterProvider.otherwise( '/upload' );


})
.config(['$httpProvider', function($httpProvider){
  // django and angular both support csrf tokens. This tells
  // angular which cookie to add to what header.
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}])


// API 
// auth
//   .login
//   .logout
// .account
// .records
//   .get
//   .list
// .transcription
.factory('api', function($http, $resource){
  function add_auth_header(data, headersGetter){
    // as per HTTP authentication spec [1], credentials must be
    // encoded in base64. Lets use window.btoa [2]
    var headers = headersGetter();
    headers['Authorization'] = ('Basic ' + btoa(data.username +
                                ':' + data.password));
  }


  return {
    auth: $resource('/api/auth\\/', {}, {
      login: { 
        method: 'POST', 
        transformRequest: add_auth_header
      },
      logout: { method: 'DELETE' }
    }),

    account: $resource('/api/account/', {}, {
      get: {
          method: 'GET'
      }
    }),

    record: $resource('/api/records/:recordId', { recordId: '@id'}, {
      list: {
        method: 'GET',
        isArray: true
      },
      get: {
        method: 'GET',
        isArray: false
      },
      remove: {
        method: 'DELETE',
        isArray: false
      }
    }),

    order: $resource('/api/orders/:orderId', { orderId: '@id' }, {
      list: {
        method: 'GET',
        isArray: true
      },
      get: {
        method: 'GET',
        isArray: false
      },
      create: {
        method: 'POST',
        isArray: false
      }
    }),

    transcription: $resource('/api/records/:recordId/pieces/', { recordId: '@id'}, {
      list: {
        method: 'GET',
        isArray: true
      }
    })
  };
})

.run( function run () {
})

.controller( 'AppCtrl', function AppCtrl ( $scope, $location, $modal, Data, api ) {
  $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
    if ( angular.isDefined( toState.data.pageTitle ) ) {
      $scope.pageTitle = toState.data.pageTitle + ' | Стенограф' ;
    }
  });

  $scope.Data = Data;
  $scope.Data.user = api.account.get();


  $scope.logout = function(){
    api.auth.logout(function(){
      $scope.Data.user = undefined;
    });
  };
  
})

;

