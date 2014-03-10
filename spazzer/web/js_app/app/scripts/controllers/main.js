'use strict';

angular.module('spazzerApp')
    .controller('MainCtrl', ["$scope","$http", "$state", function ($scope, $http, $state) {
        $scope.items = [];

        $scope.showSet = function(idx){
            $state.go('main.list', {start:idx});
        };

    }])
    .controller('ListCtrl',['$scope', '$http', '$state', '$stateParams', function($scope, $http, $state, $stateParams){
        console.log($stateParams);
        var idx = $stateParams.start;
        if(idx == "all"){
            var params = {start: ""};
        }else{
            var params = {start: idx};
        }

        $http.get("/api/collection/data", {params: params}).then(function(results){
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
                                               return item.name == name;
                                           });
            }
        };
    }])
    .controller('ArtistCtrl', ['$scope', '$http', '$state', '$stateParams', function($scope, $http, $state, $stateParams){
        $scope.$watch('selectedArtist', function(oldv, newv){
            var val = newv || oldv;
            if(val){
                $http.get(val.detail_url).then(function(results){
                    $scope.selectedArtistAlbums = results.data.items;
                });
            }
        });

        $scope.$watch('items', function(oldv, newv){
            $scope.initArtist($stateParams.artist);
        });
    }]);
