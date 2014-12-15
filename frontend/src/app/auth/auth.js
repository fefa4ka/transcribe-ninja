angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])

.config(function config( $stateProvider ) {
  $stateProvider.state("auth-login", {
    data:{ pageTitle: 'Вход с паролем' },
    onEnter: function($stateParams, $state, $modal, $resource, $log, Data, api) {
        $modal.open({
            templateUrl: "auth/auth.login.tpl.html",
            controller: ['$scope', 'Data', function($scope, Data) {
              $scope.Data = Data;

              $scope.dismiss = function() {
                $scope.$dismiss();
              };

              $scope.login = function() {
                api.auth.login({
                    username: $scope.username,
                    password: $scope.password
                }).
                $promise.
                    then(function(data){
                        $scope.$dismiss();

                        $scope.Data.user = api.account.get();
                    }).
                    catch(function(data){
                        // on incorrect username and password
                        
                        alert(data.data.detail);
                    });
              };
            }]
        }).result.then(function(result) {
            if (result) {
                $state.transitionTo("record");
            }
        });
    }
  });
})

;

