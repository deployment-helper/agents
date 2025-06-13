import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from app.services.s3_service import S3Service
from app.services.ocr_service import OCRService
from app.services.llm import LLMService
from app.config import storage_config, llm_config
from app.models import MCQOption, MCQQuestion, MCQList
from app.tools.video_creation_tool import create_video

logger = logging.getLogger(__name__)

class MCQService:
    """
    Service to handle multiple-choice question generation from documents
    """

    @staticmethod
    def _write_debug_files(project_id: str, full_prompt: str, llm_response: Any, debug_info: dict = None) -> None:
        """
        Write debug files containing the full prompt and LLM response for debugging purposes
        
        Args:
            project_id (str): The project ID
            full_prompt (str): The complete prompt sent to the LLM
            llm_response (Any): The response from the LLM
            debug_info (dict): Additional debug information
        """
        try:
            # Create debug directory
            debug_dir = os.path.join(storage_config.mcq_files_path, project_id, "debug")
            os.makedirs(debug_dir, exist_ok=True)
            
            # Generate timestamp for file naming
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Write the full prompt to file
            prompt_file = os.path.join(debug_dir, f"prompt_{timestamp}.txt")
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"MCQ GENERATION PROMPT - {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                f.write(full_prompt)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("END OF PROMPT\n")
                f.write("=" * 80 + "\n")
            
            # Write the LLM response to file
            response_file = os.path.join(debug_dir, f"response_{timestamp}.json")
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "response_type": str(type(llm_response).__name__),
                "response_content": None,
                "debug_info": debug_info or {}
            }
            
            # Try to serialize the response
            try:
                if hasattr(llm_response, 'dict'):
                    response_data["response_content"] = llm_response.dict()
                elif hasattr(llm_response, '__dict__'):
                    response_data["response_content"] = llm_response.__dict__
                else:
                    response_data["response_content"] = str(llm_response)
            except Exception as serialize_error:
                response_data["response_content"] = f"Could not serialize response: {str(serialize_error)}"
                response_data["response_str"] = str(llm_response)
            
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Write a summary file
            summary_file = os.path.join(debug_dir, f"summary_{timestamp}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"MCQ Generation Debug Summary - {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Project ID: {project_id}\n")
                f.write(f"Prompt Length: {len(full_prompt)} characters\n")
                f.write(f"Response Type: {type(llm_response).__name__}\n")
                
                if hasattr(llm_response, 'raw') and hasattr(llm_response.raw, '__len__'):
                    f.write(f"Number of MCQs Generated: {len(llm_response.raw)}\n")
                
                f.write(f"\nFiles Generated:\n")
                f.write(f"- Prompt: {prompt_file}\n")
                f.write(f"- Response: {response_file}\n")
                f.write(f"- Summary: {summary_file}\n")
                
                if debug_info:
                    f.write(f"\nAdditional Debug Info:\n")
                    for key, value in debug_info.items():
                        f.write(f"- {key}: {value}\n")
            
            logger.info(f"Debug files written to {debug_dir}")
            logger.info(f"Debug files: prompt_{timestamp}.txt, response_{timestamp}.json, summary_{timestamp}.txt")
            
        except Exception as e:
            logger.error(f"Error writing debug files: {str(e)}")
            # Don't raise the exception as this is just debug functionality

    @staticmethod
    def process_mcq_request(project_id: str, system_prompt: str, 
                          asset_files: List[str], user_prompt: str, mcq_count: int = 5) -> Dict[str, Any]:
        """
        Process an MCQ generation request
        
        Args:
            project_id (str): The project ID
            system_prompt (str): System prompt for the LLM
            asset_files (List[str]): List of S3 file URLs
            user_prompt (str): User prompt for the LLM
            mcq_count (int): Number of MCQs to generate (default: 5)
            
        Returns:
            Dict[str, Any]: Generated MCQ content
        """
        try:
            # Create project directory
            project_dir = os.path.join(storage_config.mcq_files_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Download and process each asset file
            processed_texts = []
            downloaded_files = []
            
            logger.info(f"Processing {len(asset_files)} asset files for project {project_id}")
            
            for file_url in asset_files:
                try:
                    # Download the file
                    local_path = S3Service.download_from_public_url(file_url, project_dir)
                    downloaded_files.append(local_path)
                    
                    # Extract text using OCR
                    text_content = OCRService.extract_text(local_path)
                    processed_texts.append(text_content)
                    
                    logger.info(f"Successfully processed file: {file_url}")
                except Exception as e:
                    logger.error(f"Error processing file {file_url}: {str(e)}")
            
            # Combine all extracted texts
            combined_text = "\n\n".join(processed_texts)
            
            # Generate MCQs using LLM
            mcqs: MCQList = MCQService._generate_mcqs(system_prompt, combined_text, user_prompt, mcq_count, project_id)
            
            # Debug: Check the type and structure of mcqs
            logger.info(f"Type of mcqs: {type(mcqs)}")
            logger.info(f"Type name: {type(mcqs).__name__}")
            logger.info(f"mcqs content preview: {str(mcqs)[:200]}...")
                
            logger.info(f"MCQ generation complete for project {project_id}")
            # Call the video creation tool to create a video from the MCQs

            mcq_list = mcqs.raw # Extract the raw MCQ list from the MCQList object
            video_result = create_video(
                title=f"MCQ Video - {project_id}",
                desc="Automatically generated multiple choice questions video",
                thumbnail_text="MCQ Quiz",
                thumbnail_visual_desc="Educational quiz thumbnail with question marks and colorful design",
                video_type="mcq",
                raw=mcq_list,  # Pass the MCQList object
                project_id=project_id
            )

            logger.info(f"Video creation result: {video_result}")
            # Return the results
            return {
                "project_id": project_id,
                "mcqs": mcqs,
                "processed_files": len(downloaded_files),
            }
            
        except Exception as e:
            logger.error(f"Error processing MCQ request: {str(e)}")
            raise
    
    @staticmethod
    def debug_write_mcq_data(project_id: str, prompt: str, response: Any, additional_info: dict = None) -> str:
        """
        Utility method to manually write debug files for MCQ data
        
        Args:
            project_id (str): Project identifier for file organization
            prompt (str): The prompt that was sent to the LLM
            response (Any): The response received from the LLM
            additional_info (dict): Additional debug information
            
        Returns:
            str: Path to the debug directory where files were written
        """
        MCQService._write_debug_files(project_id, prompt, response, additional_info)
        debug_dir = os.path.join(storage_config.mcq_files_path, project_id, "debug")
        return debug_dir
    
    @staticmethod
    def _generate_mcqs(system_prompt: str, document_text: str, user_prompt: str, mcq_count: int = 20, project_id: str = None) -> dict:
        """
        Generate MCQs using the LLM with structured output
        
        Args:
            system_prompt (str): System prompt for the LLM
            document_text (str): Extracted text from documents
            user_prompt (str): User prompt for the LLM
            mcq_count (int): Number of MCQs to generate
            project_id (str): Project ID for debug file naming
            
        Returns:
            dict: Generated MCQs
        """
        try:
            # Truncate document text if it's too long (context window limits)
            max_chars = 20000  # Approximate limit - adjust based on your model
            if len(document_text) > max_chars:
                document_text = document_text[:max_chars] + "...[truncated]"
            
            # Prepare content for the LLM
            full_prompt = f"""
            {system_prompt}
            
            DOCUMENT CONTENT:
            {document_text}
            
            USER QUERY:
            {user_prompt}
            
            INSTRUCTIONS:
            Generate exactly {mcq_count} multiple choice questions based on the document content.
            Each question should have between 2-6 options with exactly one correct answer.
            Ensure the questions are relevant to the document content and user query.
            """
            
            # Call the LLM for MCQ generation
            llm = LLMService(llm_config.provider, llm_config.model_name, llm_config.api_key)
            model = llm.model
            logger.info("Generating MCQs using LLM (structured output)...")
            logger.info(f"Full prompt length: {len(full_prompt)} characters")
            logger.debug(f"Full prompt content: {full_prompt[:500]}...")  # Log first 500 chars for debugging
            
            # Use structured output
            structured_llm = model.with_structured_output(MCQList)
            response = structured_llm.invoke(full_prompt)
            
            # Debug: Check what we got from the LLM
            logger.info(f"LLM response type: {type(response)}")
            logger.info(f"LLM response type name: {type(response).__name__}")
            
            # Write debug files
            debug_info = {
                "prompt_length": len(full_prompt),
                "document_text_length": len(document_text),
                "mcq_count_requested": mcq_count,
                "llm_provider": llm_config.provider,
                "llm_model": llm_config.model_name,
                "temperature": llm_config.temperature
            }
            
            if project_id:
                MCQService._write_debug_files(project_id, full_prompt, response, debug_info)
            else:
                # Fallback to a generic project ID if not provided
                fallback_project_id = f"mcq_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                MCQService._write_debug_files(fallback_project_id, full_prompt, response, debug_info)
            
            result = response
            
            return result
        except Exception as e:
            logger.error(f"Error generating MCQs: {str(e)}")
            raise
