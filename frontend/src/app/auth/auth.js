angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'auth-complete', {
    url: '/auth-complete',
    views: {
      "main": {
        controller: 'SocialAuthCompleteCtrl',
        templateUrl: 'auth/auth.complete.tpl.html'
      }
    },
    data: { 
      pageTitle: 'Вход',
      requireLogin: false
    }
  });
}])
.controller( 'SocialAuthCompleteCtrl', function AuthModalCtrl( $scope ) {
    console.log('close');
    window.close();
})

.controller( 'AuthModalCtrl', function AuthModalCtrl( $scope, $modalInstance, authCallback, $rootScope, api ) {
    $scope.authCallback = authCallback;
    $scope.logining = false;
    $scope.alerts = [];
    $scope.new_user = 1;

    $scope.popup = function (url) {
        var params = "width=650, height=450, menubar=no,location=no,resizable=no,scrollbars=no,status=no",
            auth_win = window.open(url, "Social Auth", params);

        var interval = window.setInterval(function() {
            try {
                if (auth_win == null || auth_win.closed) {
                    window.clearInterval(interval);
                    api.account.get();
                }
            }
            catch (e) {
            }
        }, 1000);
    };

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


