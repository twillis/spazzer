'use strict';

angular.module('spazzerApp')
    .factory('MusicService', ['$http', function($http){
        /*singleton style service, the "api" is that each of these methods will return promises*/
        this.getCollection = function(start){
            var params = {};

            if(start === 'all'){
                params = {start: ''};
            }else{
                params = {start: start};
            }

            return $http.get('/api/collection/data', {params: params});
        };

        this.getArtistDetail = function(artist){
            return $http.get('/api/collection/detail', {params: {artist: artist}});
        };

        return this;
    }])
    .controller('MainCtrl', ['$scope','$state', function ($scope, $state) {
        $scope.start = $state.params.start;

        $scope.$root.$on('$stateChangeSuccess', function(event, tostate, toparams){
            $scope.start = toparams.start;
        });//needed because parent view is initialized once where children are created at state transition??


        $scope.showSet = function(idx){
            $state.go('main.list', {start:idx});
            $scope.start = idx;
        };

        $scope.isSelected = function(idx){
            return $scope.start && $scope.start === idx;
        };
    }])
    .controller('ListCtrl',['$scope', 'MusicService', '$state', '$stateParams', function($scope, MusicService, $state){
        MusicService.getCollection($state.params.start).then(function(results){
            $scope.items = results.data.items;
            if($scope.items && $state.params.artist){
                $scope.selectedArtist = _.find($scope.items,
                                               function(item){
                                                   return item.name === $state.params.artist;
                                               });
            }else{
                $scope.selectedArtist = null;
            }

        });

        $scope.selectArtist = function(item){
            $scope.selectedArtist = item;
            $state.go('main.list.artist', {artist: item.name});
        };
    }])
    .controller('ArtistCtrl', ['$scope', 'MusicService', '$state', '$stateParams', function($scope, MusicService, $state){
        MusicService.getArtistDetail($state.params.artist).then(function(results){
            $scope.selectedArtistAlbums = results.data.items;
        });
    }]);
