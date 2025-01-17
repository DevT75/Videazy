import React, { useEffect } from 'react'
import { useRef, useState } from 'react'
import { useFile } from '../context/FileContext';
import axios from 'axios';
import { checkAuthenticated, downloadFile, uploadFiles, uploadFilesAuthenticated } from '../services/api';

const FileCard = ({ file, idx, handleCancel, compressionProgress }) => {
  const { compressed, setCompressed } = useFile();
  let name = file.name;
  let key = "compressed_" + name;
  // console.log(key);
  let i = 0;
  while (i > 0 && name[i] != '.') i--;
  i++;
  name = name.substring(0, i);
  return (
    <div className='relative h-24 aspect-video'>
      <div className="flex w-full h-full flex-col gap-2 justify-around items-center py-1 rounded-md">
        <video src={URL.createObjectURL(file)} className='w-full h-full border-4 rounded-sm border-orange' />
        {
          compressionProgress > 0 && compressionProgress < 100 && (
            <div className='text-white text-center text-xs w-full'>
              {`Compressing ${file.name}... ${compressionProgress}%`}
            </div>
          )}
        <button onClick={() => handleCancel(idx)} className='absolute -top-2 -right-2 px-2 py-1 bg-black text-white hover:bg-white hover:text-black hover:font-semibold transition-all duration-300 hover:shadow-[0_0_0_2px_rgba(0,0,0,1)] text-xs rounded-full'>X</button>
        {
          compressed.has(key) &&
          <a className='bg-black text-orange px-2 py-1 -mt-1 rounded-lg cursor-pointer'
            onClick={async (e) => {
              e.preventDefault();
              await downloadFile(compressed.get(key), file.name);
            }}
          >
            Download
          </a>
        }
      </div>
      {/* <p className='text-gray whitespace-nowrap text-xs'>{name}</p> */}
    </div>
  );
}


const DragDropFiles = ({ handleCancel, handleUpload }) => {
  const { files, setFiles, compressed, setCompressed } = useFile();
  const inputRef = useRef();

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFiles(e.dataTransfer.files);
  };

  useEffect(() => {
    console.log(files);
  }, [files]);

  useEffect(() => {
    console.log(compressed);
  }, [compressed])
  // send files to the server // learn from my other video



  return (
    <>
      <div
        className="w-[60%] h-[70%] flex flex-col gap-2 justify-center items-center px-6 py-6 border-dashed border-2 border-gray-400 rounded-lg"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <h1>{files.length > 0 ? "Drag and Drop Files to Add More" : "Drag and Drop Files to Upload"}</h1>
        <h1>Or</h1>
        <input
          type="file"
          multiple
          onChange={(e) => {
            setFiles(Array.from(e.target.files))
          }}
          hidden
          accept="video/mp4, video/webm, video/ogg"
          ref={inputRef}
          className=''
        />
        <button onClick={() => inputRef.current.click()} className='px-6 py-3 rounded-xl bg-orange text-white hover:bg-white hover:text-orange hover:font-semibold transition-all duration-300 hover:shadow-[0_0_0_2px]'>{!(files.length > 0) ? "Select Files" : "Add More Files"}</button>
      </div>
    </>
  );
};
const UploadFile = () => {
  const { files, setFiles, compressed, setCompressed } = useFile();
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [compressionProgress, setCompressionProgress] = useState({});

  const monitorCompressionProgress = async (fileName, setCompressionProgress) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${URL}/upload/progress/${fileName}`);
        const { data } = response.data;
        // console.log(response);w
        // console.log(data);
        const key = `compressed_${fileName}`;
        setCompressionProgress((prev) => ({
          ...prev,
          [key]: data,
        }));

        if (progress === 100) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error(`Error monitoring progress for ${fileName}:`, error);
        clearInterval(interval);
      }
    }, 1000); // Poll every second
  };

  const handleUpload = async () => {
    setLoading(true);
    const auth = await checkAuthenticated();
    let data;
    if (!auth) {
      data = await uploadFiles(files, setCompressed, setProgress, setCompressionProgress);
    }
    else {
      data = await uploadFilesAuthenticated(files, setCompressed, setProgress, setCompressionProgress);
    }
    setLoading(false);
    return data;
  };

  useEffect(() => {
    const sources = files.map((file) => {
      const fileName = file.name;
      const key = `compressed_${fileName}`;
      const url = "http://127.0.0.1:8000";
      const source = new EventSource(`${url}/upload/progress/${fileName}`);

      source.onmessage = (event) => {
        const progress = parseFloat(event.data);
        setCompressionProgress((prev) => ({
          ...prev,
          [key]: progress,
        }));

        if (progress === 100) {
          source.close();
        }
      };

      source.onerror = () => {
        console.error(`Error occurred for ${fileName}`);
        source.close();
      };

      return source;
    });

    return () => {
      sources.forEach((source) => source.close());
    };
  }, [files]);


  const handleCancel = (idx) => setFiles(prev => prev.filter((_, index) => index !== idx));

  return (
    <>
      <div className='w-[90%] pt-10 h-[60%] flex flex-row justify-center items-center px-6 gap-4'>
        <DragDropFiles handleCancel={handleCancel} handleUpload={handleUpload} />
        {
          files.length > 0 && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-* gap-4 py-4 px-4 w-[60%] border border-gray-400 overflow-y-auto h-[70%]">
                {Array.from(files).map((file, idx) => (
                  <FileCard key={idx} file={file} idx={idx} handleCancel={handleCancel} compressionProgress={compressionProgress[file.name]} />
                ))}
              </div>
            </>
          )
        }
      </div>
      {
        files.length > 0 && (
          <div className='flex flex-row gap-4 mb-20 pt-4'>
            <button onClick={() => setFiles([])} className='px-4 py-2 bg-black text-white hover:bg-white hover:text-black hover:font-semibold transition-all duration-300 hover:shadow-[0_0_0_2px_rgba(0,0,0,1)] rounded-md'>Cancel</button>
            <button onClick={handleUpload} className='px-4 py-2 bg-black text-white hover:bg-white hover:text-black hover:font-semibold transition-all duration-300 hover:shadow-[0_0_0_2px_rgba(0,0,0,1)] rounded-md'>
              {loading ? `Uploading... (${progress}%)` : "Upload"}
            </button>
          </div>)
      }

    </>
  )
}

export default UploadFile;
