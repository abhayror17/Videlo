// Ad Templates for /ads-img-gen page
// Based on Nano Banana Pro Prompt Guide

export const adTypes = [
  {
    id: 'product',
    name: 'Product Showcase',
    icon: 'package',
    description: 'E-commerce style product photography with clean backgrounds',
    promptTemplate: '{product_name} on {surface}, {lighting}, {style} product photography'
  },
  {
    id: 'social',
    name: 'Social Media Ad',
    icon: 'instagram',
    description: 'Instagram/Facebook ad formats with text overlays and CTAs',
    promptTemplate: '{style} social media ad featuring {product_name}, {composition}, text reads "{cta_text}", {lighting}, eye-catching campaign aesthetic'
  },
  {
    id: 'lifestyle',
    name: 'Lifestyle Editorial',
    icon: 'camera',
    description: 'Authentic lifestyle moments with editorial polish',
    promptTemplate: '{subject} {action} with {product_name} in {setting}, {composition}, {lighting}, authentic lifestyle photography'
  },
  {
    id: 'food',
    name: 'Food & Culinary',
    icon: 'utensils',
    description: 'Gourmet food photography for restaurants and food brands',
    promptTemplate: '{food_item} {presentation}, {composition}, {lighting}, professional food photography, {style} aesthetic'
  },
  {
    id: 'corporate',
    name: 'Corporate/Professional',
    icon: 'briefcase',
    description: 'Business headshots, team photos, office environments',
    promptTemplate: '{subject} in {setting}, {composition}, {lighting}, professional corporate photography, {style} aesthetic'
  },
  {
    id: 'marketing',
    name: 'Content/Marketing',
    icon: 'megaphone',
    description: 'Flat-lays, social templates, promotional content',
    promptTemplate: '{content_type} featuring {product_name}, {composition}, text reads "{headline}", {lighting}, modern marketing aesthetic'
  }
]

export const stylePresets = [
  {
    id: 'minimal',
    name: 'Minimal Clean',
    description: 'Clean, simple backgrounds with soft shadows',
    lighting: 'soft diffused lighting',
    surface: 'white marble surface',
    style: 'minimalist'
  },
  {
    id: 'luxury',
    name: 'Luxury Premium',
    description: 'Elegant, high-end aesthetic with dramatic lighting',
    lighting: 'dramatic spotlight with subtle rim lighting',
    surface: 'reflective black surface',
    style: 'luxury premium'
  },
  {
    id: 'lifestyle',
    name: 'Natural Lifestyle',
    description: 'Authentic, warm, approachable feel',
    lighting: 'warm natural window light',
    surface: 'rustic wooden surface',
    style: 'lifestyle'
  },
  {
    id: 'dramatic',
    name: 'Dramatic Bold',
    description: 'High contrast, eye-catching visuals',
    lighting: 'dramatic side lighting with deep shadows',
    surface: 'dark textured surface',
    style: 'cinematic'
  },
  {
    id: 'fresh',
    name: 'Fresh Bright',
    description: 'Bright, airy, optimistic mood',
    lighting: 'bright high-key lighting',
    surface: 'light concrete surface',
    style: 'fresh contemporary'
  },
  {
    id: 'editorial',
    name: 'Editorial Magazine',
    description: 'Professional magazine-quality look',
    lighting: 'professional three-point lighting',
    surface: 'seamless backdrop',
    style: 'editorial'
  }
]

export const compositionOptions = [
  { id: 'closeup', name: 'Close-up', value: 'close-up shot showing fine details' },
  { id: 'medium', name: 'Medium Shot', value: 'medium shot with context' },
  { id: 'wide', name: 'Wide Shot', value: 'wide shot showing full environment' },
  { id: 'overhead', name: 'Overhead/Flat-lay', value: 'overhead flat-lay composition' },
  { id: 'angle', name: 'Dynamic Angle', value: 'dynamic angle with depth' },
  { id: 'centered', name: 'Centered Hero', value: 'centered hero shot composition' }
]

export const lightingOptions = [
  { id: 'natural', name: 'Natural Window', value: 'soft natural window light from left' },
  { id: 'golden', name: 'Golden Hour', value: 'warm golden hour lighting' },
  { id: 'studio', name: 'Studio Soft', value: 'professional studio softbox lighting' },
  { id: 'dramatic', name: 'Dramatic', value: 'dramatic side lighting with shadows' },
  { id: 'highkey', name: 'High-Key Bright', value: 'bright high-key even lighting' },
  { id: 'rim', name: 'Rim Light', value: 'backlit with rim lighting effect' }
]

export const aspectRatios = [
  { value: '1:1', label: '1:1 Square', preview: '1/1', description: 'Instagram feed, general social' },
  { value: '9:16', label: '9:16 Portrait', preview: '9/16', description: 'Stories, Reels, TikTok' },
  { value: '16:9', label: '16:9 Landscape', preview: '16/9', description: 'YouTube, Facebook feed' },
  { value: '4:5', label: '4:5 Portrait', preview: '4/5', description: 'Instagram portrait ads' },
  { value: '4:3', label: '4:3 Standard', preview: '4/3', description: 'Presentations, displays' }
]

// Full prompt templates for each ad type with all parameters
export const fullPromptTemplates = {
  product: {
    buildPrompt: (params) => {
      const { productName, description, style, composition, lighting, surface, textOverlay } = params
      let prompt = `${productName} on ${surface}, ${composition}, ${lighting}, ${style} product photography`
      
      if (description) {
        prompt = `${description}, ${prompt}`
      }
      
      if (textOverlay) {
        prompt += `, text reads "${textOverlay}" in modern typography`
      }
      
      return prompt + ', sharp focus, professional quality'
    }
  },
  
  social: {
    buildPrompt: (params) => {
      const { productName, description, style, composition, lighting, ctaText, headline } = params
      let prompt = `Social media advertisement featuring ${productName}`
      
      if (description) {
        prompt += `, ${description}`
      }
      
      prompt += `, ${composition}, ${lighting}, ${style} aesthetic`
      
      if (headline) {
        prompt += `, bold headline "${headline}"`
      }
      
      if (ctaText) {
        prompt += `, call-to-action text "${ctaText}"`
      }
      
      return prompt + ', eye-catching, scroll-stopping design'
    }
  },
  
  lifestyle: {
    buildPrompt: (params) => {
      const { productName, subject, action, setting, style, composition, lighting } = params
      let prompt = `${subject} ${action} with ${productName}`
      
      if (setting) {
        prompt += ` in ${setting}`
      }
      
      prompt += `, ${composition}, ${lighting}, ${style} lifestyle photography, authentic moment`
      
      return prompt + ', editorial quality'
    }
  },
  
  food: {
    buildPrompt: (params) => {
      const { foodItem, presentation, style, composition, lighting, textOverlay } = params
      let prompt = `${foodItem} ${presentation}, ${composition}, ${lighting}, professional food photography`
      
      if (style) {
        prompt += `, ${style} aesthetic`
      }
      
      if (textOverlay) {
        prompt += `, text "${textOverlay}"`
      }
      
      return prompt + ', appetizing, high detail'
    }
  },
  
  corporate: {
    buildPrompt: (params) => {
      const { subject, setting, style, composition, lighting, textOverlay } = params
      let prompt = `${subject} in ${setting}, ${composition}, ${lighting}, professional corporate photography`
      
      if (style) {
        prompt += `, ${style} aesthetic`
      }
      
      if (textOverlay) {
        prompt += `, subtle branding "${textOverlay}"`
      }
      
      return prompt + ', business professional, confident'
    }
  },
  
  marketing: {
    buildPrompt: (params) => {
      const { contentType, productName, style, composition, lighting, headline, ctaText } = params
      let prompt = `${contentType} featuring ${productName}, ${composition}, ${lighting}, modern marketing aesthetic`
      
      if (style) {
        prompt += `, ${style} style`
      }
      
      if (headline) {
        prompt += `, headline text "${headline}"`
      }
      
      if (ctaText) {
        prompt += `, CTA button "${ctaText}"`
      }
      
      return prompt + ', brand-ready, campaign quality'
    }
  }
}

// Default values for each ad type
export const defaultValues = {
  product: {
    productName: 'Premium Product',
    surface: 'white marble surface',
    composition: 'centered hero shot composition',
    lighting: 'soft diffused lighting',
    style: 'minimalist clean'
  },
  social: {
    productName: 'Your Product',
    composition: 'dynamic angle with depth',
    lighting: 'bright high-key even lighting',
    style: 'contemporary',
    ctaText: 'Shop Now'
  },
  lifestyle: {
    productName: 'Product',
    subject: 'Person',
    action: 'using',
    setting: 'modern lifestyle environment',
    composition: 'medium shot with context',
    lighting: 'warm natural window light',
    style: 'authentic lifestyle'
  },
  food: {
    foodItem: 'Gourmet Dish',
    presentation: 'beautifully plated on ceramic dish',
    composition: 'close-up shot showing fine details',
    lighting: 'soft natural window light from left',
    style: 'culinary editorial'
  },
  corporate: {
    subject: 'Professional',
    setting: 'modern office environment',
    composition: 'medium shot professional framing',
    lighting: 'professional three-point lighting',
    style: 'corporate editorial'
  },
  marketing: {
    contentType: 'Promotional content',
    productName: 'Featured Product',
    composition: 'overhead flat-lay composition',
    lighting: 'bright high-key even lighting',
    style: 'modern marketing',
    headline: 'New Arrival'
  }
}

// Text rendering tips for ads
export const textRenderingTips = [
  'Keep text to 3-5 words maximum for best results',
  'Use quotation marks for exact text in prompts',
  'Specify font style: "bold sans-serif" or "elegant serif"',
  'For CTAs, use action words: "Shop Now", "Learn More", "Get Started"'
]

export default {
  adTypes,
  stylePresets,
  compositionOptions,
  lightingOptions,
  aspectRatios,
  fullPromptTemplates,
  defaultValues,
  textRenderingTips
}
