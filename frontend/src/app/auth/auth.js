angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])

.config(function config( $stateProvider ) {

})

.controller( 'AuthModalCtrl', function AuthModalCtrl( $scope, $modalInstance, authCallback, Data, api ) {
    $scope.Data = Data;
    $scope.authCallback = authCallback;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.authLogin = function() {
        var login = function () {
            api.auth.login({
                username: $scope.username,
                password: $scope.password
            }).
            $promise.
                then(function(data){
                    $modalInstance.dismiss();

                    $scope.Data.user = api.account.get();

                    // Если есть коллбэк
                    if(angular.isUndefined($scope.authCallback) === false) {
                        $scope.authCallback();
                    }
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

                $scope.Data.user = api.account.get();

                // Если есть коллбэк
                login();
            });
        } else {
            login();
        }
    };

})

;


