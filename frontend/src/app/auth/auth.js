angular.module( 'transcribe-ninja.auth', [
  'ui.router'
])
.provider('modalState', function($stateProvider) {
    var provider = this;
    this.$get = function() {
        return provider;
    };

    this.state = function(stateName, options) {
        var modalInstance;
        $stateProvider.state(stateName, {
            data: options.data,
            views: {
              'modal': {
                url: options.url,
                data: options.data
              }
            },
            onEnter: function($modal, $state) {
                    modalInstance = $modal.open(options);
                    modalInstance.result['finally'](function() {
                        modalInstance = null;
                        if ($state.$current.name === stateName) {
                            $state.go('^');
                        }
                    });
                },
                onExit: function() {
                    if (modalInstance) {
                        modalInstance.close();
                    }
                }
        });
    };
})
.config(function config( $stateProvider, modalStateProvider) {
  modalStateProvider.state("auth-login", {
    url: '^/login',
    data : {
      pageTitle: 'Вход'
    },
    templateUrl: "auth/auth.login.tpl.html",
    controller: ['$scope', 'Data', 'api', function($scope, Data, api) {
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
        
  });
})

;

