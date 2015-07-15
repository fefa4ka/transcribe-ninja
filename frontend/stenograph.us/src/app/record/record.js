angular.module( 'transcribe-ninja.record', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'record', {
    url: '/record/{recordId:int}',
    views: {
      "main": {
        controller: 'RecordCtrl',
        templateUrl: 'record/record.tpl.html'
      }
    },
    data: { 
      pageTitle: 'Ваши записи',
      requireLogin: true
    }
  });
}])

.controller( 'RecordCtrl', ["$scope", "$translate", "$modal", "$stateParams", "api", function RecordCtrl($scope, $translate, $modal, $stateParams, api) {
  $translate.use("ru");

  $scope.order = function (record) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'order/order.modal.tpl.html',
      controller: 'OrderModalCtrl',
      windowClass: 'order-bill',
      resolve: {
        record: function () {
          return record;
        }
      }
    });
  };
  
  

}]);
