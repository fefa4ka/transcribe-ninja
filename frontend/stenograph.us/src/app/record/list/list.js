angular.module( 'transcribe-ninja.record.list', [
  'transcribe-ninja.order',
  'transcribe-ninja.payment',
  'ui.router',
  'ngAudio'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'record-list', {
    url: '/records',
    views: {
      "main": {
        controller: 'RecordListCtrl',
        templateUrl: 'record/list/list.tpl.html'
      }
    },
    data:{ 
      pageTitle: 'Ваши записи',
      requireLogin: true
     }
  });
}])

.controller( 'RecordListCtrl', ["$scope", "$translate", "$modal", "$log", "api", function RecordCtrl( $scope, $translate, $modal, $log, api ) {
  $translate.use("ru");

  $scope.records = api.record.list();

  $scope.floor = Math.floor;
  $scope.upload = function() {
    $('input[type=file]').click();

  };

  $scope.remove = function ( record ) {
    record.trashed_at = Date.now();

    api.record.remove({ recordId: record.id });

    return record;
  };

  $scope.order = function (record) {
    yaCounter30919251.reachGoal('order-open');

    $modalInstance = $modal.open(
    {
      templateUrl: 'order/order.modal.tpl.html',
      controller: 'OrderModalCtrl',
      windowClass: 'order-bill',
      resolve: {
        record: function () {
          return record;
        },
        callback: function () {
          return function () {
            $scope.records = api.record.list();
          };
        }
      }
    });
  };

}])

;
