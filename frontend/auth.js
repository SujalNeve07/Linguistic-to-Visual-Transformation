// Firebase Authentication Protection  
document.addEventListener('DOMContentLoaded', () => {  
    // Firebase Configuration  
    const firebaseConfig = {  
        apiKey: "AIzaSyALf2B9y_y8-krVEwBXEC5zwfzcDyJBLRc",  
        authDomain: "facetrace-a3b02.firebaseapp.com",  
        projectId: "facetrace-a3b02",  
        storageBucket: "facetrace-a3b02.firebasestorage.app",  
        messagingSenderId: "688778782116",  
        appId: "1:688778782116:web:11408102540d8518534d31"  
    };  

    // Initialize Firebase  
    firebase.initializeApp(firebaseConfig);  

    // Check authentication state  
    firebase.auth().onAuthStateChanged((user) => {  
        const currentPath = window.location.pathname;  
        const publicPages = ['/login.html', '/register.html', '/index.html'];  

        if (!user) {  
            // User is not logged in  
            if (!publicPages.includes(currentPath)) {  
                // Redirect to login if not on a public page  
                window.location.href = 'login.html';  
            }  
        } else {  
            // User is logged in  
            if (publicPages.includes(currentPath)) {  
                // Redirect to main application if on login/register page  
                window.location.href = 'sketch_generator.html';  
            }  
        }  
    });  

    // Logout function  
    window.logout = () => {  
        firebase.auth().signOut().then(() => {  
            // Sign-out successful.  
            window.location.href = 'login.html';  
        }).catch((error) => {  
            // An error happened.  
            console.error('Logout error', error);  
        });  
    };  
});