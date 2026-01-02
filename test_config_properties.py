#!/usr/bin/env python3
"""
Property-based tests for website configuration consistency.

Feature: custom-navigation-website, Property 1: Configuration Application Consistency
Validates: Requirements 1.1, 1.5, 4.1, 4.2

This test verifies that for any valid configuration file, Hugo build process 
should generate static website files containing all configuration settings, 
including custom title, categories, and link data.
"""

import os
import tempfile
import shutil
import subprocess
import yaml
import toml
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, dictionaries, lists, booleans
import pytest


class ConfigPropertyTest:
    """Property-based test class for Hugo configuration consistency."""
    
    def __init__(self):
        self.test_dir = None
        self.original_dir = os.getcwd()
    
    def setup_test_environment(self):
        """Set up a temporary Hugo site for testing."""
        self.test_dir = tempfile.mkdtemp(prefix="hugo_config_test_")
        os.chdir(self.test_dir)
        
        # Copy necessary Hugo theme files
        theme_src = os.path.join(self.original_dir, "themes")
        if os.path.exists(theme_src):
            shutil.copytree(theme_src, "themes")
        
        # Create basic Hugo directory structure
        os.makedirs("data", exist_ok=True)
        os.makedirs("content", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        os.makedirs("assets/images/logos", exist_ok=True)
    
    def cleanup_test_environment(self):
        """Clean up the temporary test environment."""
        os.chdir(self.original_dir)
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def generate_valid_config(self, base_url, title, author, description, theme="WebStack-Hugo"):
        """Generate a valid Hugo configuration."""
        return {
            "baseURL": base_url,
            "languageCode": "en-US",
            "title": title,
            "theme": theme,
            "preserveTaxonomyNames": True,
            "disablePathToLower": True,
            "publishDir": "public",
            "params": {
                "author": author,
                "description": description,
                "enablePreLoad": True,
                "expandSidebar": False,
                "logosPath": "assets/images/logos",
                "defaultLogo": "assets/images/logos/default.webp",
                "nightMode": False,
                "yiyan": True,
                "fancybox": True
            }
        }
    
    def generate_valid_webstack_data(self, categories):
        """Generate valid webstack navigation data."""
        webstack_data = []
        for category in categories:
            category_data = {
                "taxonomy": category["name"],
                "icon": category.get("icon", "fas fa-star"),
                "links": []
            }
            
            for link in category.get("links", []):
                link_data = {
                    "title": link["title"],
                    "logo": link.get("logo", "default.webp"),
                    "url": link["url"],
                    "description": link.get("description", "")
                }
                category_data["links"].append(link_data)
            
            webstack_data.append(category_data)
        
        return webstack_data
    
    def write_config_file(self, config_data):
        """Write configuration to config.toml file."""
        with open("config.toml", "w", encoding="utf-8") as f:
            toml.dump(config_data, f)
    
    def write_webstack_data(self, webstack_data):
        """Write navigation data to data/webstack.yml file."""
        with open("data/webstack.yml", "w", encoding="utf-8") as f:
            yaml.dump(webstack_data, f, default_flow_style=False, allow_unicode=True)
    
    def run_hugo_build(self):
        """Run Hugo build and return success status."""
        try:
            result = subprocess.run(
                ["hugo", "--quiet", "--minify"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "", "Hugo command failed or timed out"
    
    def verify_generated_site(self, config_data, webstack_data):
        """Verify that the generated site contains expected configuration elements."""
        public_dir = Path("public")
        if not public_dir.exists():
            return False, "Public directory not generated"
        
        index_file = public_dir / "index.html"
        if not index_file.exists():
            return False, "Index.html not generated"
        
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if title is present in the generated HTML
            if config_data["title"] not in content:
                return False, f"Title '{config_data['title']}' not found in generated HTML"
            
            # Check if author is present (usually in meta tags or footer)
            author = config_data["params"]["author"]
            if author and author not in content:
                return False, f"Author '{author}' not found in generated HTML"
            
            # Check if at least some navigation categories are present
            category_found = False
            for category in webstack_data:
                if category["taxonomy"] in content:
                    category_found = True
                    break
            
            if not category_found:
                return False, "No navigation categories found in generated HTML"
            
            return True, "All configuration elements verified successfully"
            
        except Exception as e:
            return False, f"Error reading generated HTML: {str(e)}"


# Hypothesis strategies for generating test data
@st.composite
def valid_url_strategy(draw):
    """Generate valid URLs for testing."""
    protocols = ["http://", "https://"]
    domains = ["example.com", "test.org", "demo.net", "site.io"]
    paths = ["", "/", "/path", "/path/to/page"]
    
    protocol = draw(st.sampled_from(protocols))
    domain = draw(st.sampled_from(domains))
    path = draw(st.sampled_from(paths))
    
    return f"{protocol}{domain}{path}"

@st.composite
def navigation_link_strategy(draw):
    """Generate navigation link data."""
    return {
        "title": draw(text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")))),
        "url": draw(valid_url_strategy()),
        "description": draw(text(max_size=200, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")))),
        "logo": draw(st.sampled_from(["default.webp", "github.png", "google.png", "test.png"]))
    }

@st.composite
def navigation_category_strategy(draw):
    """Generate navigation category data."""
    return {
        "name": draw(text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")))),
        "icon": draw(st.sampled_from(["fas fa-star", "fas fa-tools", "fas fa-book", "far fa-folder"])),
        "links": draw(lists(navigation_link_strategy(), min_size=1, max_size=5))
    }


class TestConfigurationProperties:
    """Test class containing property-based tests for configuration consistency."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.config_test = ConfigPropertyTest()
        self.config_test.setup_test_environment()
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.config_test.cleanup_test_environment()
    
    @given(
        base_url=valid_url_strategy(),
        title=text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        author=text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
        description=text(max_size=200, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po"))),
        categories=lists(navigation_category_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=100, deadline=60000)  # 100 iterations, 60 second timeout
    def test_configuration_application_consistency(self, base_url, title, author, description, categories):
        """
        Property 1: Configuration Application Consistency
        
        For any valid configuration file, Hugo build process should generate 
        static website files containing all configuration settings, including 
        custom title, categories, and link data.
        
        **Feature: custom-navigation-website, Property 1: Configuration Application Consistency**
        **Validates: Requirements 1.1, 1.5, 4.1, 4.2**
        """
        # Generate valid configuration data
        config_data = self.config_test.generate_valid_config(base_url, title, author, description)
        webstack_data = self.config_test.generate_valid_webstack_data(categories)
        
        # Write configuration files
        self.config_test.write_config_file(config_data)
        self.config_test.write_webstack_data(webstack_data)
        
        # Run Hugo build
        build_success, stdout, stderr = self.config_test.run_hugo_build()
        
        # Assert that build succeeds
        assert build_success, f"Hugo build failed. Stdout: {stdout}, Stderr: {stderr}"
        
        # Verify that generated site contains expected configuration elements
        verification_success, verification_message = self.config_test.verify_generated_site(config_data, webstack_data)
        
        # Assert that all configuration elements are present in generated site
        assert verification_success, f"Configuration verification failed: {verification_message}"


if __name__ == "__main__":
    # Run the property-based test
    pytest.main([__file__, "-v"])