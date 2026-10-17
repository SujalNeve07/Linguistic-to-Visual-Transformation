import torch  
import torchvision.models as models  
import torchvision.transforms as transforms  
from PIL import Image  
import numpy as np  
import base64  
import io  
import os  
import traceback  
import logging  
import random

class ImageMatcher:  
    def __init__(self, dataset_path, max_images):  
        """  
        Initialize image matcher with dataset  
        
        Args:  
        - dataset_path: Path to the dataset directory  
        - max_images: Maximum number of images to process  
        """  
        # Configure logging  
        logging.basicConfig(level=logging.INFO)  
        self.logger = logging.getLogger(__name__)  

         
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)  
        self.model.eval()   
        
        # Feature extraction layer  
        self.feature_extractor = torch.nn.Sequential(  
            *list(self.model.children())[:-2]  # Remove last two layers  
        )  
        
        # Image transformation pipeline  
        self.transform = transforms.Compose([  
            transforms.Resize((224, 224)),  
            transforms.ToTensor(),  
            transforms.Normalize(  
                mean=[0.485, 0.456, 0.406],  
                std=[0.229, 0.224, 0.225]  
            )  
        ])  
        
        # Load dataset images  
        self.dataset_images = self._load_dataset_images(dataset_path, max_images)  
        
        # Extract features with error handling  
        self.dataset_features = self._extract_dataset_features()  
    
    def _load_dataset_images(self, dataset_path, max_images):  
        """  
        Load images from the dataset with error handling and limit  
        
        Args:  
        - dataset_path: Path to dataset directory  
        - max_images: Maximum number of images to load  
        
        Returns:  
        - List of dataset image details  
        """  
        dataset_images = []  
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp']  
        
        try:  
            # Ensure the path exists  
            if not os.path.exists(dataset_path):  
                self.logger.error(f"Dataset path does not exist: {dataset_path}")  
                return []  

            # Walk through directory  
            for root, dirs, files in os.walk(dataset_path):  
                for file in files:  
                    # Check file extension  
                    if any(file.lower().endswith(ext) for ext in supported_extensions):  
                        full_path = os.path.join(root, file)  
                        
                        try:  
                            # Verify file is a valid image  
                            with Image.open(full_path) as img:  
                                # Convert image to base64  
                                with open(full_path, "rb") as image_file:  
                                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')  
                                
                                dataset_images.append({  
                                    'path': full_path,  
                                    'base64': base64_image  
                                })  
                        except Exception as img_error:  
                            self.logger.warning(f"Could not process image {full_path}: {img_error}")  
                        
                        # Stop if we've reached max images  
                        if len(dataset_images) >= max_images:  
                            self.logger.info(f"Reached maximum image limit of {max_images}")  
                            return dataset_images  
        
        except Exception as e:  
            self.logger.error(f"Error loading dataset images: {e}")  
            return []  
        
        return dataset_images  
    
    def _extract_dataset_features(self):  
        """  
        Extract features for all dataset images with comprehensive error handling  
        
        Returns:  
        - List of feature vectors for dataset images  
        """  
        dataset_features = []  
        
        for image_data in self.dataset_images:  
            try:  
                # Open image with error handling  
                try:  
                    image = Image.open(image_data['path'])  
                except Exception as open_error:  
                    self.logger.warning(f"Could not open image {image_data['path']}: {open_error}")  
                    continue  

                # Ensure image is in RGB mode  
                if image.mode != 'RGB':  
                    image = image.convert('RGB')  
                
                # Extract features  
                features = self.extract_features(image)  
                
                if features is not None:  
                    dataset_features.append({  
                        'path': image_data['path'],  
                        'base64': image_data['base64'],  
                        'features': features  
                    })  
            except Exception as e:  
                self.logger.error(f"Error processing {image_data['path']}: {e}")  
        
        self.logger.info(f"Extracted features for {len(dataset_features)} images")  
        return dataset_features 
    
    def base64_to_image(self, base64_string):  
        """Convert base64 string to PIL Image"""  
        try:  
            # Remove data URL prefix if present  
            if base64_string.startswith('data:image'):  
                base64_string = base64_string.split(',')[1]  
            
            image_data = base64.b64decode(base64_string)  
            image = Image.open(io.BytesIO(image_data))  
            
            # Convert to RGB if the image is not already in RGB mode  
            if image.mode != 'RGB':  
                image = image.convert('RGB')  
            
            return image  
        except Exception as e:  
            print(f"Error converting base64 to image: {e}")  
            print(f"Problematic base64 string (first 50 chars): {base64_string[:50]}...")  
            return None  
    
    def extract_features(self, image):  
        """Enhanced feature extraction with multi-scale approach"""  
        try:  
            if image is None:  
                print("Image is None in feature extraction")  
                return None  
            
            # Multi-scale feature extraction  
            scales = [  
                transforms.Resize((224, 224)),  
                transforms.Resize((299, 299)),  
                transforms.Resize((384, 384))  
            ]  
            
            multi_scale_features = []  
            
            for scale in scales:  
                # Create a new transform pipeline for each scale  
                scale_transform = transforms.Compose([  
                    scale,  
                    transforms.ToTensor(),  
                    transforms.Normalize(  
                        mean=[0.485, 0.456, 0.406],  
                        std=[0.229, 0.224, 0.225]  
                    )  
                ])  
                
                # Extract features at this scale  
                input_tensor = scale_transform(image).unsqueeze(0)  
                
                with torch.no_grad():  
                    features = self.feature_extractor(input_tensor)  
                
                # Flatten and normalize features  
                features = features.squeeze().flatten()  
                features = features / np.linalg.norm(features)  
                
                multi_scale_features.append(features.numpy())  
            
            # Combine multi-scale features  
            combined_features = np.concatenate(multi_scale_features)  
            
            # Final normalization  
            combined_features = combined_features / np.linalg.norm(combined_features)  
            
            return combined_features  
        
        except Exception as e:  
            print(f"Enhanced feature extraction error: {e}")  
            print(f"Traceback: {traceback.format_exc()}")  
            return None  

    def calculate_similarity(self, features1, features2):  
        """Advanced similarity calculation with multiple metrics"""  
        try:  
            if features1 is None or features2 is None:  
                print("Features are None in similarity calculation")  
                return 0.0  
            
            # Ensure features are 1D arrays  
            features1 = np.atleast_1d(features1)  
            features2 = np.atleast_1d(features2)  
            
            # Cosine Similarity  
            cosine_sim = np.dot(features1, features2) / (  
                np.linalg.norm(features1) * np.linalg.norm(features2)  
            )  
            
            # Euclidean Distance Similarity  
            euclidean_dist = np.linalg.norm(features1 - features2)  
            euclidean_sim = 1 / (1 + euclidean_dist)  
            
            # Pearson Correlation  
            pearson_corr = np.corrcoef(features1, features2)[0, 1]  
            
            # Weighted combination of similarity metrics  
            weights = {  
                'cosine': 0.5,   # Most important  
                'euclidean': 0.3,  
                'pearson': 0.2  
            }  
            
            # Combine similarities  
            combined_similarity = (  
                weights['cosine'] * cosine_sim +  
                weights['euclidean'] * euclidean_sim +  
                weights['pearson'] * ((pearson_corr + 1) / 2)  # Normalize to 0-1  
            )  
            
            # Convert to percentage with non-linear scaling  
            similarity_percentage = max(0, min(100, (combined_similarity + 1) * 45))  
            
            return float(similarity_percentage)  
        
        except Exception as e:  
            print(f"Advanced similarity calculation error: {e}")  
            print(f"Traceback: {traceback.format_exc()}")  
            return 0.0  
   
    def match_images(
            self,
            generated_images,
            stored_images=None,
            use_members=False):

        """Enhanced image matching"""

        match_results = []

        # -------------------------------
        # Select Dataset
        # -------------------------------
        if use_members:

            members = ImageMatcher(
                r"D:\BE Final Year Project\forensic-sketch-matching\backend\datasets\members",
                max_images=500
            )

            if not members.dataset_features:
                return []

            # Pick ONE random image from members
            all_images = [random.choice(members.dataset_features)]

        else:

            # Use Humans dataset
            all_images = self.dataset_features.copy()

        # -------------------------------
        # Add stored images if provided
        # -------------------------------
        if stored_images:
            for stored_img_base64 in stored_images:
                try:
                    stored_image = self.base64_to_image(stored_img_base64)

                    if stored_image is not None:

                        stored_features = self.extract_features(stored_image)

                        if stored_features is not None:
                            all_images.append({
                                "base64": stored_img_base64,
                                "features": stored_features
                            })

                except Exception as e:
                    print(f"Error processing stored image: {e}")

        # -------------------------------
        # Match generated images
        # -------------------------------
        for gen_img_base64 in generated_images:

            gen_image = self.base64_to_image(gen_img_base64)

            if gen_image is None:
                continue

            gen_features = self.extract_features(gen_image)

            if gen_features is None:
                continue

            image_matches = []

            for image_data in all_images:

                similarity = self.calculate_similarity(
                    gen_features,
                    image_data["features"]
                )

                adaptive_threshold = 60

                if similarity >= adaptive_threshold:

                    image_matches.append({
                        "similarity_score": similarity,
                        "image": image_data.get("base64", ""),
                        "path": image_data.get("path", "Unknown")
                    })

            image_matches.sort(
                key=lambda x: x["similarity_score"],
                reverse=True
            )

            match_results.append({
                "generated_image": gen_img_base64,
                "matches": image_matches[:5]
            })

        return match_results
# Singleton instance
image_matcher = ImageMatcher(
    r"D:\BE Final Year Project\forensic-sketch-matching\backend\datasets\Humans",
    max_images=500
)