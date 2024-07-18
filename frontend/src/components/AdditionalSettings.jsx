import { useState } from "react"
import { FaChevronDown } from "react-icons/fa6";
import { FaChevronUp } from "react-icons/fa6";

const AdditionalSettings = () => {
  const [isOpen,setIsOpen] = useState(false);
  return (
    <div className={`w-[60%] ${isOpen ? "rounded-none h-full" : "rounded-md h-[10%]"} bg-gray flex flex-col justify-start items-center`}>
      <div className="flex flex-row justify-between items-center w-full">
        <h2 className="text-white text-semibold text-xl mt-5 ml-6">Advance Settings (Optional)</h2>
        {
          isOpen ? (
            <FaChevronUp size={24} className="text-orange mr-6 mt-5 cursor-pointer" onClick={()=>setIsOpen((prev)=>!prev)}/>
          ):
          (
            <FaChevronDown size={24} className="text-orange mr-6 mt-5 cursor-pointer" onClick={()=>setIsOpen((prev)=>!prev)}/>

          )
        }
      </div>
    </div>
  )
}

export default AdditionalSettings
