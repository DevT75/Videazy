import { useState, createContext, useEffect,useContext } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
    const [files, setFiles] = useState(new Array());
    const [compressed,setCompressed] = useState(new Map());
    return (
        <FileContext.Provider value={{ files, setFiles,compressed,setCompressed }}>
            {children}
        </FileContext.Provider>
    );
}


export const useFile = () => useContext(FileContext);

