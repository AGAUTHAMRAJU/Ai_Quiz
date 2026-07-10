/*=========================================
AiQuiz Home Page
=========================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*==============================
    Counter Animation
    ==============================*/

    const counters = document.querySelectorAll(".counter");

    const observer = new IntersectionObserver(function(entries){

        entries.forEach(function(entry){

            if(entry.isIntersecting){

                const counter = entry.target;

                const target = parseInt(counter.dataset.target);

                if(isNaN(target)) return;

                let count = 0;

                const speed = Math.ceil(target / 80);

                const timer = setInterval(function(){

                    count += speed;

                    if(count >= target){

                        counter.innerHTML = target + "+";

                        clearInterval(timer);

                    }

                    else{

                        counter.innerHTML = count;

                    }

                },20);

                observer.unobserve(counter);

            }

        });

    },{

        threshold:.5

    });

    counters.forEach(function(counter){

        observer.observe(counter);

    });

    /*==============================
    Card Animation
    ==============================*/

    const cards=document.querySelectorAll(

        ".mini-card,.about-card,.feature-card,.workflow-card,.contact-card"

    );

    cards.forEach(function(card){

        card.addEventListener("mouseenter",function(){

            card.style.transform="translateY(-10px)";

        });

        card.addEventListener("mouseleave",function(){

            card.style.transform="translateY(0px)";

        });

    });

    /*==============================
    Active Navbar
    ==============================*/

    const sections=document.querySelectorAll("section");

    const navLinks=document.querySelectorAll(".navbar .nav-link");

    window.addEventListener("scroll",function(){

        let current="";

        sections.forEach(function(section){

            const sectionTop=section.offsetTop-120;

            if(window.scrollY>=sectionTop){

                current=section.getAttribute("id");

            }

        });

        navLinks.forEach(function(link){

            link.classList.remove("active");

            const href=link.getAttribute("href");

            if(href && href==="#"+current){

                link.classList.add("active");

            }

        });

    });

    /*==============================
    Reveal Animation
    ==============================*/

    const reveal=document.querySelectorAll(

        ".about-card,.feature-card,.workflow-card,.contact-card,.mini-card"

    );

    const revealObserver=new IntersectionObserver(function(entries){

        entries.forEach(function(entry){

            if(entry.isIntersecting){

                entry.target.style.opacity="1";

                entry.target.style.transform="translateY(0px)";

            }

        });

    },{

        threshold:.2

    });

    reveal.forEach(function(item){

        item.style.opacity="0";

        item.style.transform="translateY(40px)";

        item.style.transition=".8s";

        revealObserver.observe(item);

    });

});