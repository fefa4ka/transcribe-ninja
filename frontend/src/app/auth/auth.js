angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])

.config(function config( $stateProvider ) {

})

.controller( 'AuthModalCtrl', function AuthModalCtrl( $scope, $modalInstance, authCallback, $rootScope, api ) {
    $scope.authCallback = authCallback;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.new_user = 1;

    $scope.authLogin = function() {
        var login = function () {
            api.auth.login({
                username: $scope.username,
                password: $scope.password
            }).
            $promise.
                then(function(data){
                    $modalInstance.dismiss();

                    api.account.get().
                        $promise.
                        then(function(data) {
                            if(angular.isUndefined(data.id)) {
                                $rootScope.currentUser = undefined;
                            } else {
                                $rootScope.currentUser = data;
                                // Если есть коллбэк
                                if(angular.isUndefined($scope.authCallback) === false) {
                                    $scope.authCallback();
                                }
                            }
                        });

                    
                });
            };

        // Если новый, то регистрируем
        if($scope.new_user == 1) {
            api.auth.register({
                username: $scope.username,
                email: $scope.username,
                password: $scope.password
            }).$promise.
            then(function(data){
                $modalInstance.dismiss();
                login();
            });

            // Ya.Metrica
            yaCounter27735045.reachGoal('registration');
        } else {
            login();

            // Ya.Metrica
            yaCounter27735045.reachGoal('login');
        }
    };

})

;


