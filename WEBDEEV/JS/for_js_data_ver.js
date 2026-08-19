console.log("Hii , iam tanmoy");
    let a = 1;
    let b = 5;
    let k = 8;
    console.log(a+b+k);
    console.log(typeof a,typeof b,typeof k);
    {
        a = 34
        a = a + 1
        console.log(a)
    }
    console.log(a);
    const a=7;
    let name = "Harry";
    let name = "CodeWithHarry"; // This will throw an error
    let a = 10;
    let b = 20;
    let sum = a + b; // 30
    console.log(sum);
    
    let str1 = "Code";
    let str2 = "WithHarry";
    let fullStr = str1 + str2; // "CodeWithHarry"
    console.log(fullStr);
    
    let x="Tanmoty Dutta ";
    let y=54;
    let z=3.45;
    const p =true;
    let q = undefined;
    let f =null;
    let d=NaN;
    console.log(x,y,z,p,q,f,d);
    console.log(typeof x,typeof y,typeof z,typeof p,typeof q,typeof f,typeof d);
    // why typeof null = "object" ?



    //Object
    let o ={
        "Name":"Tanmoy",
        "Job Code" :5600
    }
    console.log(o);
    o.salary=55000
    console.log(o);
    o.ishandsome=true
    console.log(o);
    // The result of typeof null is "object". That’s an officially  
    // recognized error in typeof, coming from very early days of 
    // JavaScript and kept for compatibility. Definitely, null is not an
    // object. It is a special value with a separate type of its own. The 
    // behavior of typeof is wrong here.
``