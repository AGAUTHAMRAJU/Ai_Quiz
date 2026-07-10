/*=========================================
AiQuiz Dashboard
=========================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*=====================================
    Counter Animation
    =====================================*/

    const counters = document.querySelectorAll(".counter");

    const counterObserver = new IntersectionObserver(function(entries){

        entries.forEach(function(entry){

            if(entry.isIntersecting){

                const counter = entry.target;

                const target = Number(counter.dataset.target);

                if(isNaN(target)) return;

                let current = 0;

                const increment = Math.max(1, Math.ceil(target / 80));

                const timer = setInterval(function(){

                    current += increment;

                    if(current >= target){

                        current = target;

                        clearInterval(timer);

                    }

                    counter.innerHTML = current;

                },20);

                counterObserver.unobserve(counter);

            }

        });

    },{

        threshold:.5

    });

    counters.forEach(function(counter){

        counterObserver.observe(counter);

    });

    /*=====================================
    Card Hover
    =====================================*/

    document.querySelectorAll(".stat-card").forEach(function(card){

        card.addEventListener("mouseenter",function(){

            card.style.transform="translateY(-8px) scale(1.02)";

        });

        card.addEventListener("mouseleave",function(){

            card.style.transform="translateY(0px) scale(1)";

        });

    });

    /*=====================================
    Fade Animation
    =====================================*/

    const observer = new IntersectionObserver(function(entries){

        entries.forEach(function(entry){

            if(entry.isIntersecting){

                entry.target.style.opacity = "1";

                entry.target.style.transform = "translateY(0px)";

            }

        });

    },{

        threshold:.15

    });

    document.querySelectorAll(

        ".stat-card,.quick-actions,.dashboard-hero,.card"

    ).forEach(function(item){

        item.style.opacity="0";

        item.style.transform="translateY(35px)";

        item.style.transition=".7s";

        observer.observe(item);

    });

    /*=====================================
    Welcome Message
    =====================================*/

    const hour = new Date().getHours();

    let greeting = "Welcome Back";

    if(hour < 12){

        greeting = "Good Morning ☀️";

    }

    else if(hour < 17){

        greeting = "Good Afternoon 🌤️";

    }

    else{

        greeting = "Good Evening 🌙";

    }

    const badge = document.querySelector(".dashboard-hero .badge");

    if(badge){

        badge.innerHTML = greeting;

    }

    /*=====================================
    Progress Animation
    =====================================*/

    document.querySelectorAll(".progress-bar").forEach(function(bar){

        const value = bar.dataset.value;

        if(value){

            setTimeout(function(){

                bar.style.width = value + "%";

            },300);

        }

    });

    /*=====================================
    Button Ripple Effect
    =====================================*/

    document.querySelectorAll(".btn").forEach(function(btn){

        btn.addEventListener("click",function(e){

            const ripple=document.createElement("span");

            const rect=btn.getBoundingClientRect();

            const size=Math.max(rect.width,rect.height);

            ripple.style.width=size+"px";

            ripple.style.height=size+"px";

            ripple.style.left=(e.clientX-rect.left-size/2)+"px";

            ripple.style.top=(e.clientY-rect.top-size/2)+"px";

            ripple.className="ripple";

            btn.appendChild(ripple);

            setTimeout(function(){

                ripple.remove();

            },600);

        });

    });

});
