'use strict';

angular.module('spazzerApp')
    .factory('MusicService', 
             ['$http', 
              function($http){
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
    .factory('Audio', function($document){
        this.audio = $document[0].createElement('audio');
        return this;
    })
    .factory('MusicPlayer', 
             ['MusicPlayList',
              'Audio',
              '$rootScope',
              function(MusicPlayList, Audio, $rootScope){
                  this.playing = false;
                  this.playList = MusicPlayList;
                  this.currentPosition = null;

                  this.playToggle = function(){
                      if(!this.playing){
                          Audio.audio.play();
                      }else{
                          Audio.audio.pause();
                      }
                      this.playing = !this.playing;
                  };

                  this.playNext = function(){
                      var new_idx = _.indexOf(this.playList.playList, this.playList.current) + 1;
                      this.playItemByIndex(new_idx);
                  };

                  this.playPrevious = function(){
                      var new_idx = _.indexOf(this.playList.playList, this.playList.current) - 1;
                      this.playItemByIndex(new_idx);
                  };

                  this.playItem = function(item){
                      Audio.audio.src = item.download_url;
                      Audio.audio.play();
                      this.playList.setCurrent(item);
                      this.playing = true;
                  };

                  this.playItemByIndex = function(idx){
                      var new_item = this.playList.playList[idx];
                      if(!new_item){
                          Audio.audio.pause();
                          this.playing = false;
                      }else{
                          this.playItem(new_item);
                      }
                      
                  };

                  
                  var service = this;

                  $rootScope.$on('$itemRemoved',
                                 //if current is removed, stop playing.
                                 function(){
                                     if(!service.playList.current){
                                         Audio.audio.pause();
                                         Audio.audio.src = null;
                                         service.playing = false;
                                     }
                                 });

                  Audio.audio.addEventListener('ended', function(){
                      $rootScope.$apply(function(){
                          service.playNext();
                      });
                  }, false);

                  Audio.audio.addEventListener('timeupdate', function(){
                      $rootScope.$apply(function(){
                          service.currentPosition = (Audio.audio.currentTime / Audio.audio.duration) * 100;
                      });
                  }, false);
                  return this;
              }])
    .factory('MusicPlayList',
             ['$rootScope',
              function($rootScope){
                 this.playList = [];
                 this.current = null;

                 var _is = function(idx){
                     return function(item){
                         return item && idx && item.$$hashKey === idx.$$hashKey;
                     };
                 };

                 this.find_item = function(idx){
                     return _.find(this.playList, _is(idx));
                 };


                 this.addItem = function(item){
                     this.playList.push(item);
                 };
                 this.addAll = function(items){
                     this.playList = _.union(this.playList, items);
                 };
                 this.removeItem = function(idx){
                     this.playList = _.reject(this.playList, _is(idx));
                     if(_is(idx)(this.current)){
                         this.current = null;
                     }
                     $rootScope.$broadcast('$itemRemoved', idx);
                 };
                 this.setCurrent = function(idx){
                     this.current = this.find_item(idx);
                     if(!this.current){
                         this.addItem(idx);
                         this.current = idx;
                     }
                 };
                 return this;
             }])
    .controller('PlayerCtrl',
                ['$scope', 
                 '$state', 
                 'MusicPlayer', 
                 'MusicPlayList', 
                 function($scope, $state, MusicPlayer, MusicPlayList){
                     $scope.playList = MusicPlayList;
                     $scope.player = MusicPlayer;
                     
                 }])
    .controller('MainCtrl', 
                ['$scope',
                 '$state', 
                 function ($scope, $state) {
                     $scope.start = $state.params.start;

                     $scope.$root.$on('$stateChangeSuccess', function(event, tostate, toparams){
                         $scope.start = toparams.start;
                     });//needed because parent view is initialized once where children are created at state transition??


                     $scope.showSet = function(idx){
                         $state.go('collection.list', {start:idx});
                         $scope.start = idx;
                     };

                     $scope.isSelected = function(idx){
                         return $scope.start && $scope.start === idx;
                     };
                 }])
    .controller('ListCtrl',
                ['$scope', 
                 'MusicService', 
                 '$state', 
                 '$stateParams', 
                 function($scope, MusicService, $state){
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
                         $state.go('collection.list.artist', {artist: item.name});
                     };
                 }])
    .controller('ArtistCtrl', 
                ['$scope', 
                 'MusicService', 
                 '$state', 
                 'MusicPlayList', 
                 function($scope, MusicService, $state, MusicPlayList){
                     $scope.playList = MusicPlayList;
                     MusicService.getArtistDetail($state.params.artist).then(function(results){
                         $scope.selectedArtistAlbums = results.data.items;
                     });
                 }]);
