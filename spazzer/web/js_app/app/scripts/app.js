'use strict';
angular.module('spazzerApp', [
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ui.router'
  ]).config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/list');
    $stateProvider.state('collection',
                         {url: '/list',
                          templateUrl: 'views/main.html',
                          controller: 'MainCtrl'});
    $stateProvider.state('collection.list',
                         {url:'/:start',
                         templateUrl: 'views/list.html',
                         controller: 'ListCtrl'});
    $stateProvider.state('collection.list.artist',
                        {url:'/:artist',
                        templateUrl: 'views/artist.html',
                        controller: 'ArtistCtrl'});
   $stateProvider.state('player',
                        {url:'/player',
                        templateUrl: 'views/player.html',
                        controller: 'PlayerCtrl'});
  }]);
