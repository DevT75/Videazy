import UploadFile from './UploadFile'
import AdditionalSettings from './AdditionalSettings'
import { FileProvider } from '../context/FileContext'

export const Home = () => {
  return (
    <FileProvider>
      <div className='w-full h-[90vh] bg-white flex flex-col justify-center items-center'>
        <UploadFile />
      </div>
      <div className='h-[90vh] w-full bg-white flex flex-col justify-start items-center -mt-24'>
        <AdditionalSettings />
      </div>

    </FileProvider>

  )
}
