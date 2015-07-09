angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])

.config(function config( $stateProvider ) {

})

.controller( 'AuthModalCtrl', function AuthModalCtrl( $scope, $modalInstance, authCallback, $rootScope, api ) {
    $scope.authCallback = authCallback;
    $scope.logining = false;
    $scope.alerts = [];
    $scope.new_user = 1;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    
    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    };

    $scope.authLogin = function() {
        var login = function () {
            $scope.logining = true;

            api.auth.login({
                username: $scope.username,
                password: $scope.password
            }, function(data){
                    $modalInstance.dismiss();

                    api.account.get({}, function (data) {
                        $rootScope.currentUser = data;
                        // Если есть коллбэк
                        if(angular.isUndefined($scope.authCallback) === false) {
                            $scope.authCallback();
                        }
                    });  
            }, function (data) {
                $rootScope.currentUser = undefined;
                $scope.logining = false;
                
                $scope.alerts.push({ type: 'danger', msg: 'Неправильный логин или пароль' });
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


