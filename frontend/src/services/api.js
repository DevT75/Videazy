import axios from "axios"

const URL = import.meta.env.API_URL || "https://videazy-r6c3dizosq-em.a.run.app";

export const uploadFiles = async (files, setCompressed) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }
    // console.log(formData);
    try {
        const response = await axios.post(`${URL}/upload/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        console.log(response.data);
        for (let i = 0; i < response.data.length; i++) setCompressed(map => new Map(map.set(response.data[i].filename, response.data[i].url)));
    } catch (error) {
        console.error("Error uploading files:", error);
    }
};

export const downloadFile = async (url, filename) => {
    try {
        console.log('Starting download for:', `${URL}${url}`);

        const response = await axios.get(`${URL}${url}`, {
            responseType: 'blob'
        });

        console.log('Response received:', response.status);

        if (response.status !== 200) {
            throw new Error('Network response was not ok');
        }

        const blob = new Blob([response.data]);
        console.log('Blob created, initiating download');

        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = `compressed_${filename}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(blobUrl);
        a.remove();

        console.log('Download initiated');
    } catch (error) {
        console.error('Download failed:', error);
    }
};

// export const