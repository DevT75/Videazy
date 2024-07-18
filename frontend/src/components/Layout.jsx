/* eslint-disable react/display-name */
/* eslint-disable react-refresh/only-export-components */
// eslint-disable-next-line react/prop-types
import { useState } from "react";
import { CiMenuBurger } from "react-icons/ci";
import Stagger from "./Stagger";

export default ({ children }) => {
    const [clicked,setClicked] = useState(false);
    return (
        <div className="min-h-screen w-full filter-custom-filter overflow-x-hidden flex flex-col justify-center items-center">
            {/* <Stagger/> */}
            <div className="fixed z-10 w-[90%] mt-3 bg-black rounded-xl h-8 top-0 flex flex-row justify-between items-center py-8 md:px-6 px-2 backdrop-blur-lg shadow-md">
                <div className="p-2.5 w-60 items-center justify-center flex text-white text-2xl">Videazy</div>
                {
                    <CiMenuBurger className="lg:hidden" size={24} onClick={() => setClicked(!clicked)}/>
                }
                {
                    <div className="lg:flex p-1 hidden lg:w-1/5 lg:block lg:flex-row justify-around items-center">
                        {/* <button className="py-3 px-6 bg-black text-white hover:bg-white hover:text-black hover:font-semibold border-2 border-black">Login</button>
                        <button className="py-3 px-6 bg-black text-white hover:bg-white hover:text-black hover:font-semibold border-2 border-black">Signup</button> */}
                        {/* <button className="rounded-xl px-6 py-2 text-[#4c4d4c] hover:bg-[#3d3d3d] hover:text-white transition-all duration-300 hover:shadow-[0_0_0_2px_rgba(0,0,0,1)]">Login</button>
                        <button className="rounded-xl px-6 py-2 text-[#4c4d4c] hover:bg-[#4c4c4c] hover:text-white transition-all duration-300 hover:shadow-[0_0_0_2px_rgba(0,0,0,1)]">Signup</button> */}
                        <button className="rounded-xl px-6 py-2 text-white hover:bg-gray hover:text-orange transition-all duration-300">Login</button>
                        <button className="rounded-xl px-6 py-2 text-white hover:bg-gray hover:text-orange transition-all duration-300">Signup</button>
                    </div>
                }
            </div>
            {/* <div className="absolute w-full h-full -z-1 bg-black">
            </div> */}
            {children}
            <div className="fixed z-10 w-full h-8 bottom-0 flex flex-row justify-center items-center py-8 md:px-8 px-4 bg-black backdrop-blur-lg shadow-md">
                <div className="p-2.5 w-60 items-center justify-center flex text-white text-2xl">
                    Footer
                </div>
            </div>
        </div>
    )
}
