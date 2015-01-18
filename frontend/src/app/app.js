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
.config(function($translateProvider) {
    $translateProvider.translations('ru', {
        'Стенограф': 'Transcribe',
        HEADLINE: 'Hello there, This is my awesome app!',
        INTRO_TEXT: 'And it has i18n support!',
          "{{num}} second": "{{num}} секунда",
        "{{num}} seconds":  "{{num}} секунд",
        "{{num}} minute": "{{num}} минута",
        "{{num}} minutes":  "{{num}} минут",
        "{{num}} hour":   "{{num}} час",
        "{{num}} hours":  "{{num}} часов",
        "{{num}} day":    "{{num}} day",
        "{{num}} days":   "{{num}} days",
        "{{num}} week":   "{{num}} week",
        "{{num}} weeks":  "{{num}} weeks",
        "{{num}} month":  "{{num}} month",
        "{{num}} months": "{{num}} months",
        "{{num}} year":   "{{num}} year",
        "{{num}} years":  "{{num}} years"
    });
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

    queue: $resource('/api/queue/', {}, {
      get: {
        method: 'GET'
      },
      create: {
        method: 'POST'
      }
    }),

    transcription: $resource('/api/transcriptions\\/:transcriptionId', { transcriptionId: '@id' }, {
      list: {
        method: 'GET'
      },
      create: {
        method: 'POST'
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

    order: $resource('/api/orders\\/', {}, {
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
    })
  };
})

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

