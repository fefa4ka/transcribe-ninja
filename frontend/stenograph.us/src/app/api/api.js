angular.module( 'transcribe-ninja.api', [
  'ngResource'
])
.config(function($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
})
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
        url: "/api/auth/register\\/",
        method: 'POST'
      },
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
}]);