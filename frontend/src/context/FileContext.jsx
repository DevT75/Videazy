import { useState, createContext, useEffect,useContext } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
    const [files, setFiles] = useState(new Array());

    return (
        <FileContext.Provider value={{ files, setFiles }}>
            {children}
        </FileContext.Provider>
    );
}


export const useFile = () => useContext(FileContext);

