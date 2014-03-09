'use strict';

angular.module('spazzerApp')
  .controller('MainCtrl', ["$scope","$http", function ($scope, $http) {
      $scope.items = [];

      $scope.showSet = function(idx){
          console.log(idx);
          if(idx == "all"){
              var params = {start: ""};
          }else{
              var params = {start: idx};
          }
          $http.get("/api/collection/data", {params: params}).then(function(results){
              $scope.items = results.data.items;
              $scope.selectedArtistAlbums = null;
          });
      };

      $scope.selectArtist = function(item){
          $http.get(item.detail_url).then(function(results){
             $scope.selectedArtistAlbums = results.data.items;
          });
      };
  }]);
