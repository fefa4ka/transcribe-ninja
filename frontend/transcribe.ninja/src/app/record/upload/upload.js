angular.module( 'transcribe-ninja.record.upload', [
  'transcribe-ninja.player',
  'ui.router',
  'angularFileUpload'
  ])

.config(function config( $stateProvider ) {
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
})

.filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
}])

.directive('tnGetDuration', function (Data) {
  return {
    link: function (scope, element, attrs) {
      element.on('canplaythrough', function (e) {
        scope.item.formData[0].duration = e.target.duration;
        scope.$apply();
      });
    }
  };
})

.controller( 'RecordUploadCtrl', function RecordUploadCtrl($scope, $translate, $modal, FileUploader, $log, Data, api ) {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  var uploader = $scope.uploader = new FileUploader({
    url: '/api/records/',
    alias: 'audio_file',
    headers : {
        'X-CSRFToken': getCookie('csrftoken') // X-CSRF-TOKEN is used for Django Tokens
    }
  }),
    authModal = $scope.authModal;

  $modalInstance = {};

  $scope.Data = Data;

  console.log('suka blya');
  $scope.open = function(){
    $modalInstance = $modal.open({
      templateUrl: 'record/upload/upload.list.tpl.html',
      windowClass: 'upload-modal',
      controller: function($scope, $modalInstance, $log, Data, uploader){
        $scope.uploader = uploader;
        $scope.Data = Data;

        $scope.startUpload = function () {
          console.log('lalla');
          if (typeof $scope.Data.user.id == "undefined") {
            var callback = function () {
              // Обновляем CSRF Token после авторизации
              var token = getCookie('csrftoken'),
                  items = uploader.getNotUploadedItems();

              uploader.headers['X-CSRFToken'] = token;

              for(var index in items) {
                items[index].headers['X-CSRFToken'] = token;
              }
              console.log( uploader.getNotUploadedItems(), uploader.headers['X-CSRFToken']);

              uploader.uploadAll();
            };

            console.log('startUpload');
            authModal(callback);
          } else {
            uploader.uploadAll();
          }
        };

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');

          uploader.cancelAll();
        };
    },
    resolve: {
        uploader: function () {
          return uploader;
        }
      },
      size: 'lg'
    });
  };

  uploader.playerInit = function () {
    console.log('player init', $scope);
    $scope.wavesurfer.on('ready', function() {
      console.log('wavesurfer load', $scope.wavesurfer);
    });
  };

  uploader.onWhenAddingFileFailed = function(item /*{File|FileLikeObject}*/, filter, options) {
      console.info('onWhenAddingFileFailed', item, filter, options);
  };

  uploader.onAfterAddingFile = function(fileItem) {
      console.info('onAfterAddingFile', fileItem);

      fileItem.formData.push({
          title: fileItem.file.name.replace(/\.[^/.]+$/, ""),
          speakers: 2,
          file: URL.createObjectURL(fileItem._file),
          duration: 0
      });

  };
  uploader.onAfterAddingAll = function(addedFileItems) {
      $scope.open();

      // console.info('onAfterAddingAll', addedFileItems);
  };
  
  uploader.onCompleteAll = function() {
      uploader.queue = [];
      $modalInstance.dismiss('cancel');
  };

})

;
