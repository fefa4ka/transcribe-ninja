angular.module( 'transcribe-ninja.record.upload', [
  'ngAudio',
  'ui.router',
  'angularFileUpload'
  ])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'record-upload', {
    url: '/upload',
    views: {
      "main": {
        controller: 'RecordUploadCtrl',
        templateUrl: 'record/upload/upload.tpl.html'
      }
    },
    data: { 
      pageTitle: 'Загрузка записи',
      requireLogin: false
     }
  });
}])

.filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
}])

// .directive('tnGetDuration', function () {
//   return {
//     link: function (scope, element, attrs) {
//       element.on('canplaythrough', function (e) {
//         scope.item.formData[0].duration = e.target.duration;
//         scope.$apply();
//       });
//     }
//   };
// })

.controller( 'RecordUploadCtrl', ["$scope", "$rootScope", "$translate", "$modal", "FileUploader", "$state", "api", "ngAudio", function RecordUploadCtrl($scope, $rootScope, $translate, $modal, FileUploader, $state, api, ngAudio ) {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  var uploader = $rootScope.uploader = $scope.uploader = new FileUploader({
    url: '/api/records/',
    alias: 'audio_file',
    headers : {
        'X-CSRFToken': getCookie('csrftoken') // X-CSRF-TOKEN is used for Django Tokens
    }
  }),
    authModal = $scope.authModal;

  $modalInstance = {};
  $scope.modal = {};

  $scope.open = function(){
    yaCounter30919251.reachGoal('upload-open');

    $modalInstance = $modal.open({
      templateUrl: 'record/upload/upload.list.tpl.html',
      windowClass: 'upload-modal',
      controller: ["$scope", "$modalInstance", "$log", "$rootScope", "uploader", function($scope, $modalInstance, $log, $rootScope, uploader){
        $scope.uploader = uploader;
        
        $scope.sound = ngAudio.load($scope.uploader.queue[0].formData[0].file);

        $scope.startUpload = function () {
          yaCounter30919251.reachGoal('upload-started');

          $scope.uploader.queue[0].formData[0].duration = $scope.sound.duration;

          // Если не залогинен логинимся
          if (angular.isUndefined($rootScope.currentUser)) {
            var callback = function () {
              // Обновляем CSRF Token после авторизации
              var token = getCookie('csrftoken'),
                  items = uploader.getNotUploadedItems();

              uploader.headers['X-CSRFToken'] = token;

              // Обновляем у всех файлов, просто у объекта не достаточно
              for(var index in items) {
                items[index].headers['X-CSRFToken'] = token;
              }

              uploader.uploadAll();
            };

            
            authModal(callback);
          } else {
            uploader.uploadAll();
          }
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
          uploader.clearQueue();
        };
    }],
    resolve: {
        uploader: function () {
          return uploader;
        }
      },
      size: 'md'
    });

    $scope.modal = $modalInstance;
  };



  // uploader.onWhenAddingFileFailed = function(item /*{File|FileLikeObject}*/, filter, options) {
  //     console.info('onWhenAddingFileFailed', item, filter, options);
  // };

  uploader.onAfterAddingFile = function(fileItem) {

      fileItem.formData.push({
          title: fileItem.file.name.replace(/\.[^/.]+$/, ""),
          speakers: 2,
          file: URL.createObjectURL(fileItem._file),
          duration: 0
      });

  };

  uploader.onWhenAddingFileFailed = function(item, filter, options) {
    console.log(item, filter, options);
  };

  uploader.onAfterAddingAll = function(addedFileItems) {

      $scope.open();

      // console.info('onAfterAddingAll', addedFileItems);
  };
  
  uploader.onSuccessItem = function(item, response, status, headers) {
    uploader.clearQueue();

    $modalInstance.dismiss();
    $scope.modal.dismiss();

    $state.go('record-list', { });

    $scope.$parent.records = api.record.list();

    yaCounter30919251.reachGoal('upload-finished');
  };



}])

;
