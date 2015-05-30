var app = angular.module('web', ['ngAnimate']);

app.controller('Accueil', function($scope, $http){
	$http.post('http://localhost:5000/', "").success(function(data, status) {
		$scope.bienvenue = data[0];
		data.shift();
		$scope.rubriques = data;		
	}).error(function(data){
	});
});

app.controller('Concert', function($scope, $http){

	$http.post('http://localhost:5000/Concert', {'type': "all"}).success(function(data){
		$scope.concerts = data;

		dates_dup = [];
		cat_dup = [];
		for(i in data){
			dates_dup.push(data[i].date.substring(0,7)+"-01");
			cat_dup.push(data[i].style);
		}
		$scope.dates = suppDoubles(dates_dup);
		$scope.styles = suppDoubles(cat_dup);

	}).error(function(data){

	});

	$scope.filtre = 'all';
	$scope.modifFiltre = function(filt){
		$scope.filtre = filt;
	};

	suppDoubles = function(tab){
		res = [];
		for(i in tab){
			if(tab.indexOf(tab[i]) == i){
				res.push(tab[i]);
			}
		}
		return(res);
	}

});

app.controller('Connexion', function($scope, $http, $window){
	$scope.valid = true;
	$scope.user = {'username': '', 'password': ''};

	$scope.submit = function(){
		if($scope.user.username === '' || $scope.user.password === ''){
			$scope.valid = false;
			return;
		}
		else {
			$http.post('http://localhost:5000/Authenticate', $scope.user)
				.success(function(data){
					$scope.valid = true;
					$window.sessionStorage.token = data.token;
				})
				.error(function(data){
					$scope.valid = false;
					delete $window.sessionStorage.token;
				})
		}
		
	}

	$scope.isConnected = function(){
		if($window.sessionStorage.token){
			return(true);
		}
		else {
			return(false);
		}
	}

	$scope.disconnect = function(){
		delete $window.sessionStorage.token;
		$window.location.href = "http://localhost:5000/";
	}

	$scope.connect = function(){
		$window.location.href = "http://localhost:5000/Connexion";
	}

});

app.controller('Private', function($http, $scope, $window, $filter){
	$scope.tarif = {'enfant': null, 'etudiant': null, 'plein': null};
	$scope.image = {'titre': null, 'chemin': null};
	$scope.video = {'titre': null, 'chemin': null};
	$scope.concert = {'titre': null, 'date': null, 'description': null, 'auteur': null, 'horaire': null, 'lieu': null, 'participation': null, 'tarif': $scope.tarif, 'style': null, 'image': $scope.image, 'video': $scope.video, 'nb_places': null, 'reservable': null};

	$scope.newConcert = function(){
		$http.post('http://localhost:5000/newConcert', $scope.concert)
		.success(function(data){
			alert("Ajout effectué");
		})
		.error(function(data, status){
			if(status === 401){
				alert("Accès refusé");
			}
			if(status === 403){
				alert("Authentification expirée");
			}
			delete $window.sessionStorage.token;
			$window.location.href = "http://localhost:5000/Connexion";
		});
	};

	
});

app.controller('Clean', function($http, $scope, $window, $filter){
	$scope.cleanConcert = function(){
		date = {'date': $filter('date')(new Date(), 'yyyy-MM-dd')};
		
		$http.post('http://localhost:5000/cleanConcert', date)
		.success(function(data){
			alert("Nettoyage effectué");
		})
		.error(function(data, status){
			if(status === 401){
				alert("Accès refusé");
			}
			if(status === 403){
				alert("Authentification expirée");
			}
			delete $window.sessionStorage.token;
			$window.location.href = "http://localhost:5000/Connexion";
		});
	};

	$http.post('http://localhost:5000/Concert', {'type': "all"})
	.success(function(data){
		$scope.concerts = data;
	})
	.error(function(data){
	});

	$scope.suppConcert = function(){
		concertToDel = [];
		for(i in $scope.concerts){
			if($scope.concerts[i].deplie === true){
				concertToDel.push({'id': $scope.concerts[i].id});
			}
		}
		if(concertToDel.length !== 0){
			$http.post('http://localhost:5000/suppConcert', concertToDel)
			.success(function(data){
				alert("Concerts supprimés");
				$window.location.href = "http://localhost:5000/Suppression";
			})
			.error(function(data, status){
				if(status === 401){
					alert("Accès refusé");
				}
				if(status === 403){
					alert("Authentification expirée");
				}
				delete $window.sessionStorage.token;
				$window.location.href = "http://localhost:5000/Connexion";
			});
		}		
	};

});

app.factory('authInterceptor', function ($rootScope, $q, $window) {
  return {
    request: function (config) {
      config.headers = config.headers || {};
      if ($window.sessionStorage.token) {
        config.headers.Authorization = $window.sessionStorage.token;
      }
      return config;
    },
    response: function (response) {
      if (response.status === 401) {
        delete $window.sessionStorage.token;
      }
      return response || $q.when(response);
    }
  };
});

app.config(function ($httpProvider) {
  $httpProvider.interceptors.push('authInterceptor');
});
