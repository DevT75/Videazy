// import axios from "axios"

// const URL = import.meta.env.ENV == "development" ? "http://localhost:8000" : "https://videazy-r6c3dizosq-em.a.run.app";

const URL = "http://127.0.0.1:8000";

console.log(URL);

// export const uploadFiles = async (files, setCompressed) => {
//     const formData = new FormData();
//     for (let i = 0; i < files.length; i++) {
//         formData.append("files", files[i]);
//     }
//     // console.log(formData);
//     try {
//         const response = await axios.post(`${URL}/upload/`, formData, {
//             headers: {
//                 'Content-Type': 'multipart/form-data'
//             }
//         });
//         console.log(response.data);
//         for (let i = 0; i < response.data.length; i++) setCompressed(map => new Map(map.set(response.data[i].filename, response.data[i].url)));
//     } catch (error) {
//         console.error("Error uploading files:", error);
//     }
// };

// export const downloadFile = async (url, filename) => {
//     try {
//         console.log('Starting download for:', `${URL}${url}`);

//         const response = await axios.get(`${URL}${url}`, {
//             responseType: 'blob'
//         });

//         console.log('Response received:', response.status);

//         if (response.status !== 200) {
//             throw new Error('Network response was not ok');
//         }

//         const blob = new Blob([response.data]);
//         console.log('Blob created, initiating download');

//         const blobUrl = window.URL.createObjectURL(blob);
//         const a = document.createElement('a');
//         a.style.display = 'none';
//         a.href = blobUrl;
//         a.download = `compressed_${filename}`;
//         document.body.appendChild(a);
//         a.click();
//         window.URL.revokeObjectURL(blobUrl);
//         a.remove();

//         console.log('Download initiated');
//     } catch (error) {
//         console.error('Download failed:', error);
//     }
// };

import axios from 'axios';

// Upload files with progress tracking
// export const uploadFiles = async (files, setCompressed, setProgress, setCompressionProgress) => {
//     const formData = new FormData();
//     files.forEach((file) => formData.append('files', file));

//     try {
//         const response = await axios.post(`${URL}/upload/`, formData, {
//             headers: { 'Content-Type': 'multipart/form-data' },
//             onUploadProgress: (progressEvent) => {
//                 const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
//                 setProgress(progress);
//             },
//         });

//         // Process compression progress for each file
//         const tasks = response.data.map(async (fileData) => {
//             const { filename, progress_url } = fileData;
//             const key = `task_${filename}`;
//             console.log(progress_url)
//             return new Promise((resolve) => {
//                 compressVideo(`task_${filename}` /*progress_url.split('/').pop()*/, (progress) => {
//                     setCompressionProgress((prev) => ({
//                         ...prev,
//                         [key]: progress, // Update compression progress per file
//                     }));

//                     // When compression completes
//                     if (progress === 100) {
//                         setCompressed((prev) => new Map(prev.set(filename, fileData.download_url)));
//                         resolve();
//                     }
//                 });
//             });
//         });

//         // Wait for all compression tasks to complete
//         await Promise.all(tasks);

//         // setCompressed(new Map(Object.entries(response.data.compressed)));
//         // return response.data;
//     } catch (error) {
//         console.error('Error uploading files:', error);
//     }
// };

export const checkAuthenticated = async () => {
    try {
        const response = await axios.post(`${URL}/users/me`);
        return response.status === 200;
    } catch (error) {
        console.error('Error checking authentication:', error);
    }
}

// export const compressVideo = async (taskId, onProgress) => {
//     try {
//         const eventSource = new EventSource(`${URL}/upload/progress/${taskId}`);

//         eventSource.onmessage = (event) => {
//             const progress = parseFloat(event.data);

//             console.log('Compression progress:', progress);

//             // onProgress(progress);

//             // If progress reaches 100, close the connection
//             if (progress === 100) {
//                 eventSource.close();
//             }
//         };

//         eventSource.onerror = (error) => {
//             console.error('Error in compression progress stream:', error);
//             eventSource.close();
//         };
//     } catch (error) {
//         console.error('Error tracking compression progress:', error);
//     }
// };

// Upload files with progress tracking
export const uploadFiles = async (files, setCompressed, setProgress, setCompressionProgress) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    try {
        const response = await axios.post(`${URL}/upload/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
                const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setProgress(progress); // Update upload progress
            },
        });

        // Process compression progress for each file
        const tasks = response.data.map(async (fileData) => {
            const { filename, progress_url } = fileData;
            // Use the taskId from the server response to track progress via SSE
            return new Promise((resolve) => {
                compressVideo(filename, (progress) => {
                    setCompressionProgress((prev) => ({
                        ...prev,
                        [filename]: progress, // Update per-file compression progress
                    }));

                    // When compression completes, update the state with download URL
                    if (progress === 100) {
                        setCompressed((prev) => new Map(prev.set(filename, fileData.download_url)));
                        resolve();
                    }
                });
            });
        });

        // Wait for all compression tasks to complete
        await Promise.all(tasks);

    } catch (error) {
        console.error('Error uploading files:', error);
    }
};

// Track video compression progress using SSE
export const compressVideo = async (taskId, onProgress) => {
    try {
        const eventSource = new EventSource(`${URL}/upload/progress/${taskId}`);

        eventSource.onmessage = (event) => {
            const progress = parseFloat(event.data); // Parse progress from SSE data
            console.log(`Compression progress for ${taskId}: ${progress}%`);

            // Call the callback function to update progress in the state
            onProgress(progress);

            // If progress reaches 100, close the connection
            if (progress === 100) {
                eventSource.close();
            }
        };

        eventSource.onerror = (error) => {
            console.error('Error in compression progress stream:', error);
            eventSource.close(); // Ensure the connection is closed on error
        };
    } catch (error) {
        console.error('Error tracking compression progress:', error);
    }
};



export const uploadFilesAuthenticated = async (files, setCompressed, setProgress, setCompressionProgress) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    try {
        const response = await axios.post(`${URL}/me`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
                const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setProgress(progress);
            },
        });

                // Process compression progress for each file
        const tasks = response.data.map(async (fileData) => {
            const { filename, progress_url } = fileData;
            return new Promise((resolve) => {
                compressVideo( `${filename}` /*progress_url.split('/').pop()*/, (progress) => {
                    setCompressionProgress((prev) => ({
                        ...prev,
                        [filename]: progress, // Update compression progress per file
                    }));

                    // When compression completes
                    if (progress === 100) {
                        setCompressed((prev) => new Map(prev.set(filename, fileData.download_url)));
                        resolve();
                    }
                });
            });
        });

        // Wait for all compression tasks to complete
        await Promise.all(tasks);

        // setCompressed(new Map(Object.entries(response.data.compressed)));
        // return response.data;
    } catch (error) {
        console.error('Error uploading files:', error);
    }
};

// Download files with progress tracking
export const downloadFile = async (url, fileName/*, onProgress*/) => {
    try {
        const response = await axios.get(`${URL}${url}`, {
            responseType: 'blob',
            onDownloadProgress: (progressEvent) => {
                const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                // onProgress(progress);
            },
        });

        const blob = new Blob([response.data]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = fileName;
        link.click();
    } catch (error) {
        console.error('Error downloading file:', error);
    }
};
