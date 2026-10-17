import os  
import random  
import cv2  
import numpy as np  

class DatasetManager:  
    def __init__(self, dataset_path):  
        """  
        Initialize dataset manager  
        
        Args:  
        - dataset_path: Path to the dataset directory  
        """  
        # Validate dataset path  
        if not os.path.exists(dataset_path):  
            raise ValueError(f"Dataset path does not exist: {dataset_path}")  
        
        self.dataset_path = dataset_path  
        self.image_paths = self._get_image_paths()  
    
    def _get_image_paths(self):  
        """  
        Collect all image paths in the dataset  
        
        Returns:  
        - List of full image paths  
        """  
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp']  
        image_paths = []  
        
        try:  
            for filename in os.listdir(self.dataset_path):  
                file_path = os.path.join(self.dataset_path, filename)  
                
                # Check if it's a file and has supported extension  
                if (os.path.isfile(file_path) and   
                    any(filename.lower().endswith(ext) for ext in supported_extensions)):  
                    image_paths.append(file_path)  
            
            # Sort paths for consistent ordering  
            image_paths.sort()  
            
            return image_paths  
        
        except Exception as e:  
            print(f"Error collecting image paths: {e}")  
            return []  
    
    def get_dataset_summary(self):  
        """  
        Generate dataset summary  
        
        Returns:  
        - Dictionary with dataset statistics  
        """  
        return {  
            'total_images': len(self.image_paths),  
            'image_paths': self.image_paths  
        }  
    
    def load_image(self, image_path, target_size=(224, 224)):  
        """  
        Load and preprocess a single image  
        
        Args:  
        - image_path: Path to the image file  
        - target_size: Resize dimensions  
        
        Returns:  
        - Preprocessed image numpy array  
        """  
        try:  
            # Read image in BGR (OpenCV default)  
            img = cv2.imread(image_path)  
            
            # Check if image is loaded successfully  
            if img is None:  
                print(f"Failed to load image: {image_path}")  
                return None  
            
            # Convert BGR to RGB (if needed for ML models)  
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
            
            # Resize image  
            img_resized = cv2.resize(img_rgb, target_size)  
            
            # Normalize to 0-1 range  
            img_normalized = img_resized / 255.0  
            
            return img_normalized  
        
        except Exception as e:  
            print(f"Error processing {image_path}: {e}")  
            return None  
    
    def shuffle_dataset(self):  
        """  
        Randomly shuffle image paths  
        
        Returns:  
        - Shuffled list of image paths  
        """  
        random.shuffle(self.image_paths)  
        return self.image_paths  
    
    def split_dataset(self, train_ratio=0.8, shuffle=True):  
        """  
        Split dataset into training and validation sets  
        
        Args:  
        - train_ratio: Proportion of dataset for training  
        - shuffle: Whether to shuffle before splitting  
        
        Returns:  
        - Dictionary with train and validation image paths  
        """  
        if shuffle:  
            self.shuffle_dataset()  
        
        total_images = len(self.image_paths)  
        train_count = int(total_images * train_ratio)  
        
        return {  
            'train': self.image_paths[:train_count],  
            'validation': self.image_paths[train_count:]  
        }  
    
    def filter_images(self, min_size=(100, 100)):  
        """  
        Filter images based on minimum size  
        
        Args:  
        - min_size: Minimum (width, height) for images  
        
        Returns:  
        - List of image paths meeting size criteria  
        """  
        filtered_paths = []  
        for path in self.image_paths:  
            try:  
                img = cv2.imread(path)  
                if (img.shape[1] >= min_size[0] and  # width  
                    img.shape[0] >= min_size[1]):    # height  
                    filtered_paths.append(path)  
            except Exception as e:  
                print(f"Error checking image {path}: {e}")  
        
        return filtered_paths  

# Example Usage  
def main():  
    # Path to your dataset  
    dataset_path = r'D:\BE Final Year Project\forensic-sketch-matching\backend\datasets\Humans'  
    
    try:  
        # Initialize DatasetManager  
        dataset_manager = DatasetManager(dataset_path)  
        
        # Get dataset summary  
        summary = dataset_manager.get_dataset_summary()  
        print(f"Total Images: {summary['total_images']}")  
        
        # Split dataset  
        dataset_splits = dataset_manager.split_dataset()  
        print(f"Training Images: {len(dataset_splits['train'])}")  
        print(f"Validation Images: {len(dataset_splits['validation'])}")  
        
        # Load and preprocess a sample image  
        sample_image_path = dataset_splits['train'][0]  
        processed_image = dataset_manager.load_image(sample_image_path)  
        
        if processed_image is not None:  
            print(f"Processed Image Shape: {processed_image.shape}")  
    
    except Exception as e:  
        print(f"An error occurred: {e}")  

if __name__ == "__main__":  
    main()