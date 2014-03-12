'use strict';

angular.module('spazzerApp')
    .controller('MainCtrl', ['$scope','$http', '$state', '$stateParams', function ($scope, $http, $state, $stateParams) {
        $scope.items = [];
        $scope.start = $stateParams.start;

        $scope.showSet = function(idx){
            $state.go('main.list', {start:idx});
          };

        $scope.initStart = function(start){
            $scope.start = start;
        };

      }])
    .controller('ListCtrl',['$scope', '$http', '$state', '$stateParams', function($scope, $http, $state, $stateParams){
        var idx = $stateParams.start;
        var params = null;
        $scope.initStart(idx);

        if(idx === 'all'){
          params = {start: ''};
        }else{
          params = {start: idx};
        }

        $http.get('/api/collection/data', {params: params}).then(function(results){
            $scope.items = results.data.items;
            $scope.selectedArtistAlbums = null;
          });

        $scope.selectArtist = function(item){
          $scope.selectedArtist = item;
          $state.go('main.list.artist', {artist: item.name});
        };

        $scope.initArtist = function(name){
            if($scope.items && name){
              $scope.selectedArtist = _.find($scope.items,
                                           function(item){
                                                return item.name === name;
                                              });
            }
          };
      }])
    .controller('ArtistCtrl', ['$scope', '$http', '$state', '$stateParams', function($scope, $http, $state, $stateParams){
        $scope.initStart($stateParams.start);
        $scope.$watch('selectedArtist', function(oldv, newv){
            var val = newv || oldv;
            if(val){
              $http.get(val.detail_url).then(function(results){
                    $scope.selectedArtistAlbums = results.data.items;
                  });
            }
          });

        $scope.$watch('items', function(){
            $scope.initArtist($stateParams.artist);
          });
      }]);
