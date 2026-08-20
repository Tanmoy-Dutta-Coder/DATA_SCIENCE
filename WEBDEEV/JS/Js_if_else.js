console.log("hello");
let age = 16;
age++;
let grace=2;

//OPERATERS
console.log(age+grace);
console.log(age-grace);
console.log(age*grace);
console.log(age/grace);
console.log(age**grace);
console.log(agegrace);
age += grace
console.log("new age",age);

//COMPARE OPERATER
console.log(188 == 4);//false
console.log(18 != 4);//true
console.log(18 == "18");//true
console.log(18 === "18");//false
console.log(18 == !"18");//false
console.log(18 !== "18");//true
console.log(18 > "18");//false
console.log(18 < "18");//false
console.log(18 < 10);//false
console.log(18 < 19);//true
console.log(18 <= 19);//true
console.log(18 <= 18);//true

//LOGICAL AND
if (age == 18 && age > 15) {
    console.log("yes your age is ", age);
}
else {
    console.log("no");

}

//LOGICAL OR

if (age == 18 || age > 15) {
    console.log("yes your age is ", age);
}
else {
    console.log("no");

}

//if else if else


if (age == 18) {
    console.log("yes your age is ", age);
}
else if(age >15){
    console.log("nahi chalega age",age)
}
else {
    console.log("no");

}

// TERNARY OPERATER

let a=8;
let b=4;
let c= a>b?(a-b):(b-a)
console.log("using ternary opt the value of c is ",c);

