angular.module( 'transcribe-ninja.api', [
  'ngResource'
])

// API 
.factory('api', ["$http", "$resource", function($http, $resource){
  function add_auth_header(data, headersGetter){
    // as per HTTP authentication spec [1], credentials must be
    // encoded in base64. Lets use window.btoa [2]
    var headers = headersGetter();
    headers['Authorization'] = ('Basic ' + btoa(data.username +
                                ':' + data.password));
  }


  return {
    auth: $resource("/api/auth/basic/", {}, {
      register: {
        url: "/api/auth/register/",
        method: 'POST'
      },
      password_reset: {
        url: "/api/auth/password/reset/",
        method: 'POST'
      },
      login: { 
        method: 'POST', 
        transformRequest: add_auth_header
      },
      logout: { 
        method: 'DELETE' 
      }
    }),

    account: $resource('/api/auth/me/', {}, {
      get: {
        method: 'GET'
      }
    }),

    statistics: $resource('/api/statistics/', {}, {
      get: {
        method: 'GET'
      }
    }),

    queue: $resource('/api/queue/', {}, {
      get: {
        url: '/api/queue/:queueId',
        method: 'GET'
      },
      create: {
        method: 'POST'
      }
    }),

    history: $resource('/api/history/', {}, {
      list: {
        method: 'GET',
        isArray: false
      },
      get: {
        method: 'GET',
        isArray: false
      }
    }),

    payment: $resource('/api/payments/', {}, {
      list: {
        method: 'GET',
        isArray: false
      },
      create: {
        method: 'POST',
        isArray: false
      }
    }),

    transcription: $resource('/api/transcriptions/:transcriptionId', { transcriptionId: '@id' }, {
      list: {
        method: 'GET'
      },
      create: {
        method: 'POST'
      }
    })
  };
}]);