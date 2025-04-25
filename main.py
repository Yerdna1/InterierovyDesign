# ai_interior_design.py

import streamlit as st
# Removed torch, transformers, diffusers imports from global scope
from PIL import Image, ImageDraw, ImageFont
import io
import base64
# Keep numpy and cv2 as they are generally lighter and might be used elsewhere
import numpy as np
import cv2
import os
from datetime import datetime
import sys
import warnings

# Potlačenie varovaní
warnings.filterwarnings('ignore')

# Konfigurácia stránky
st.set_page_config(
    page_title="AI Interior Design Generator",
    page_icon="🏠",
    layout="wide"
)

# Kontrola potrebných knižníc
try:
    import timm
    import accelerate
except ImportError:
    st.error("""
    ⚠️ Chýbajú potrebné knižnice. 
    
    Pre správne fungovanie aplikácie prosím nainštalujte:
    ```
    pip install timm accelerate
    ```
    
    Po inštalácii reštartujte aplikáciu.
    """)
    st.stop()

# Inicializácia modelov (cache na zrýchlenie)
@st.cache_resource
def initialize_models():
    """Inicializuje potrebné AI modely"""
    # Import heavy libraries inside the function
    import torch
    from transformers import DetrImageProcessor, DetrForObjectDetection
    from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
    
    try:
        # Stable Diffusion pre generovanie návrhov
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-1",
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        
        # Optimalizácia schedulera pre rýchlejšie generovanie
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        pipe = pipe.to(device)
        
        # Detekcia objektov pre analýzu miestnosti
        processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50").to(device)
        
        return pipe, processor, model, device
    except Exception as e:
        st.error(f"Chyba pri inicializácii modelov: {str(e)}")
        st.stop()

def detect_room_objects(image, processor, model):
    """Detekuje objekty v miestnosti"""
    # Import torch inside the function
    import torch
    
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    
    # Spracovanie výstupov
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.7)[0]
    
    detected_objects = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        detected_objects.append({
            "object": model.config.id2label[label.item()],
            "confidence": round(score.item(), 3),
            "box": box
        })
    
    return detected_objects

def draw_boxes(image, objects):
    """Označí detekované objekty na obrázku"""
    draw = ImageDraw.Draw(image)
    
    for obj in objects:
        box = obj["box"]
        label = f"{obj['object']} ({obj['confidence']:.2f})"
        
        # Nakreslenie obdĺžnika
        draw.rectangle(box, outline="red", width=2)
        
        # Pridanie popisku
        draw.text((box[0], box[1] - 10), label, fill="red")
    
    return image

def generate_design(image, prompt, style, strength=0.75):
    """Generuje nový dizajn interiéru pomocou Stable Diffusion"""
    # Import torch inside the function
    import torch
    
    pipe, _, _, device = initialize_models()
    
    # Vytvorenie promptu
    full_prompt = f"interior design photo, {style} style, {prompt}, professional photography, high quality, 8k resolution, beautiful lighting"
    negative_prompt = "ugly, tiling, poorly drawn, deformed, blurry, low quality, watermark, text"
    
    # Konverzia obrázka pre model
    image = image.convert("RGB")
    image = image.resize((512, 512))  # Zmenšíme pre rýchlejšie generovanie
    
    # Generovanie nového dizajnu
    with torch.inference_mode():
        result = pipe(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            image=image,
            strength=strength,
            guidance_scale=7.5,
            num_inference_steps=30  # Znížený počet krokov pre rýchlejšie generovanie
        ).images[0]
    
    return result

def suggest_furniture(style, room_type):
    """Navrhne nábytok pre danú miestnosť a štýl"""
    furniture_suggestions = {
        "modern": {
            "living_room": [
                "Modulárna sedačka v neutrálnych farbách",
                "Minimalistický konferenčný stolík so sklom",
                "LED stojacia lampa s dimérom",
                "Floating TV stojan",
                "Abstraktné umenie na stenu"
            ],
            "bedroom": [
                "Platform posteľ s čalúneným čelom",
                "Závesné nočné stolíky",
                "Vstavaná skriňa s posuvnými dverami",
                "Minimalistická toaletka",
                "Smart osvetlenie s ovládaním cez aplikáciu"
            ],
            "kitchen": [
                "Vysokolesklá kuchynská linka",
                "Ostrovček s barovou časťou",
                "Integrované spotrebiče",
                "LED podsvietenie pracovnej plochy",
                "Dotykové batérie"
            ]
        },
        "scandinavian": {
            "living_room": [
                "Svetlá látková sedačka",
                "Drevený konferenčný stolík",
                "Hygge kreslá s dekami",
                "Drevené police na stenu",
                "Prírodné rastliny v keramických kvetináčoch"
            ],
            "bedroom": [
                "Drevená posteľ s prírodným vzhľadom",
                "Biele nočné stolíky s drevenými nohami",
                "Otvorený šatník s drevenými policami",
                "Pletené koberčeky",
                "Závesné papierové lampy"
            ],
            "kitchen": [
                "Biele skrinky s drevenými úchytkami",
                "Drevená pracovná doska",
                "Otvorené police z prírodného dreva",
                "Pastelové spotrebiče",
                "Jednoduché závesné svetlá"
            ]
        },
        "industrial": {
            "living_room": [
                "Kožená Chesterfield sedačka",
                "Kovový konferenčný stolík na kolieskach",
                "Oceľové regály",
                "Vintage priemyselné svietidlá",
                "Tehlová stena (pravá alebo tapeta)"
            ],
            "bedroom": [
                "Kovová posteľ s čiernym rámom",
                "Nočné stolíky z oceľových píp",
                "Otvorený kovový šatník",
                "Edison žiarovky",
                "Hrubý vlnený koberec"
            ],
            "kitchen": [
                "Nerezové pracovné plochy",
                "Otvorené kovové police",
                "Priemyselné závesné svetlá",
                "Čierne matné skrinky",
                "Kovové barové stoličky"
            ]
        }
    }
    
    return furniture_suggestions.get(style, {}).get(room_type, ["Momentálne nemáme návrhy pre túto kombináciu"])

# Kontrola potrebných knižníc
try:
    import timm
except ImportError:
    st.error("""
    ⚠️ Knižnica 'timm' nie je nainštalovaná. 
    
    Pre správne fungovanie aplikácie prosím nainštalujte:
    ```
    pip install timm
    ```
    
    Po inštalácii reštartujte aplikáciu.
    """)
    st.stop()

# Hlavné rozhranie
st.title("🏠 AI Interior Design Generator")
st.write("Transformujte vašu miestnosť pomocou AI - jednoducho nahrajte fotku a vyberte štýl!")

# Bočný panel s nastaveniami
with st.sidebar:
    st.header("⚙️ Nastavenia")
    
    style = st.selectbox(
        "Vyberte štýl dizajnu",
        ["modern", "scandinavian", "industrial", "minimalist", "bohemian", "traditional", "luxury", "rustic"],
        index=0
    )
    
    room_type = st.selectbox(
        "Typ miestnosti",
        ["living_room", "bedroom", "kitchen", "bathroom", "office", "dining_room"],
        index=0
    )
    
    strength = st.slider(
        "Intenzita zmeny (0.0 = žiadna zmena, 1.0 = úplná zmena)",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05
    )
    
    custom_prompt = st.text_area(
        "Vlastný popis (voliteľné)",
        placeholder="Napr.: pridaj veľké okná, viac prírodného svetla, zelené rastliny...",
        height=100
    )
    
    st.markdown("---")
    st.info("""
    **Tipy pre najlepšie výsledky:**
    - Použite fotky v dobrom osvetlení
    - Snažte sa zachytiť celú miestnosť
    - Vyčistite priestor od nepotrebných predmetov
    - Uistite sa, že fotka nie je rozmazaná
    """)

# Hlavný obsah
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Originálna fotka")
    uploaded_file = st.file_uploader("Nahrajte fotku vašej miestnosti", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # Analýza miestnosti
        if st.button("🔍 Analyzovať miestnosť"):
            with st.spinner("Analyzujem objekty v miestnosti..."):
                _, processor, model, device = initialize_models()
                objects = detect_room_objects(image, processor, model)
                
                # Zobrazenie detekovaných objektov
                image_with_boxes = draw_boxes(image.copy(), objects)
                st.image(image_with_boxes, use_container_width=True)
                
                st.write("### Detekované objekty:")
                for obj in objects:
                    st.write(f"- {obj['object']} (konfidencia: {obj['confidence']:.2f})")

with col2:
    st.subheader("✨ Nový dizajn")
    
    if uploaded_file is not None:
        if st.button("🎨 Generovať nový dizajn"):
            with st.spinner("Generujem nový dizajn... (môže to trvať 1-2 minúty)"):
                try:
                    generated_image = generate_design(image, custom_prompt, style, strength)
                    st.image(generated_image, use_container_width=True)
                    
                    # Možnosť stiahnuť výsledok
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    byte_img = buf.getvalue()
                    
                    st.download_button(
                        label="💾 Stiahnuť dizajn",
                        data=byte_img,
                        file_name=f"interior_design_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"Chyba pri generovaní: {str(e)}")
    else:
        st.info("👈 Najprv nahrajte fotku miestnosti")

# Návrhy nábytku
if uploaded_file is not None:
    st.markdown("---")
    st.subheader("🛋️ Odporúčaný nábytok")
    
    suggestions = suggest_furniture(style, room_type)
    
    cols = st.columns(3)
    for i, item in enumerate(suggestions):
        with cols[i % 3]:
            st.markdown(f"- {item}")

# Galéria príkladov (vylepšené)
st.markdown("---")
st.subheader("🖼️ Príklady transformácií")

example_cols = st.columns(3)
examples = [
    {
        "before": "living_room_before.jpg",
        "after": "living_room_after.jpg",
        "style": "Modern",
        "description": "Transformácia obývačky na moderný minimalistický priestor"
    },
    {
        "before": "bedroom_before.jpg",
        "after": "bedroom_after.jpg",
        "style": "Scandinavian",
        "description": "Premena spálne na útulný škandinávsky štýl"
    },
    {
        "before": "kitchen_before.jpg",
        "after": "kitchen_after.jpg",
        "style": "Industrial",
        "description": "Kuchyňa v industriálnom štýle"
    }
]

for i, example in enumerate(examples):
    with example_cols[i]:
        st.markdown(f"**{example['style']}**")
        st.caption(example['description'])
        # Tu by ste mohli pridať skutočné príklady obrázkov
        st.image("https://via.placeholder.com/300x200.png?text=Pred", caption="Pred")
        st.image("https://via.placeholder.com/300x200.png?text=Po", caption="Po")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Vytvorené s ❤️ pomocou Streamlit a Stable Diffusion</p>
    <p>Pre najlepšie výsledky odporúčame GPU s min. 8GB VRAM</p>
</div>
""", unsafe_allow_html=True)

# Požiadavky pre spustenie (súčasť dokumentácie)
"""
Požiadavky na inštaláciu:
1. Vytvorte virtuálne prostredie:
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate  # Windows

2. Nainštalujte požadované knižnice:
   pip install streamlit torch torchvision transformers diffusers pillow opencv-python numpy timm accelerate

3. Spustite aplikáciu:
   streamlit run ai_interior_design.py

4. Otvorte webovú stránku v prehliadači (zvyčajne http://localhost:8501)

Poznámka: Pre plnú funkcionalitu je potrebná GPU s podporou CUDA.
Pre modely bez GPU môžete použiť nižšiu kvalitu alebo menšie modely.

Ak máte problémy so spustením, skúste:
- pip install --upgrade streamlit
- pip install --upgrade torch torchvision
- pip install --upgrade transformers diffusers
"""
