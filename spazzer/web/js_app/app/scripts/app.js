'use strict';
angular.module('spazzerApp', [
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ui.router',
    'ui.sortable'
  ]).config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/list');
    $stateProvider.state('collection',
                         {url: '/list',
                          templateUrl: 'views/main.html',
                          controller: 'MainCtrl'});
    $stateProvider.state('collection.search',
                         {url: '/search/:criteria',
                          templateUrl: 'views/results.html',
                          controller: 'SearchCtrl'});
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
   $stateProvider.state('admin',
                        {url:'/admin',
                        templateUrl: 'views/admin.html',
                        controller: 'AdminCtrl'});


  }]);
