'use strict';

angular.module('spazzerApp', [
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ui.router'
]).config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider.state('main',
                         {url: '/',
                          templateUrl: 'views/main.html',
                          controller: 'MainCtrl'});
    $stateProvider.state('main.list',
                         {url:'list/:start',
                         templateUrl: 'views/list.html',
                         controller: 'ListCtrl'});
    $stateProvider.state('main.list.artist',
                        {url:'/:artist',
                        templateUrl: 'views/artist.html',
                        controller: 'ArtistCtrl'});
}]);
