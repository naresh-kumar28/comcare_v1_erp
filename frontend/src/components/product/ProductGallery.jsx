import React, { useState } from 'react';

export const ProductGallery = ({ mainImage, galleryImages = [] }) => {
  const [activeImage, setActiveImage] = useState(mainImage);

  const allImages = [
    ...(mainImage ? [{ id: 'main', image: mainImage, alt_text: 'Main View' }] : []),
    ...galleryImages,
  ];

  const currentSrc = activeImage || mainImage;

  return (
    <div className="space-y-4">
      {/* Main Image Frame */}
      <div className="aspect-[4/3] w-full rounded-2xl bg-white border border-slate-200 overflow-hidden relative shadow-xs">
        {currentSrc ? (
          <img
            src={currentSrc}
            alt="Product View"
            className="w-full h-full object-contain p-4 transition-all duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-300 font-medium">
            No Image Available
          </div>
        )}
      </div>

      {/* Thumbnails */}
      {allImages.length > 1 && (
        <div className="flex items-center space-x-3 overflow-x-auto pb-2">
          {allImages.map((item, idx) => (
            <button
              key={item.id || idx}
              onClick={() => setActiveImage(item.image)}
              className={`w-16 h-16 rounded-xl border-2 overflow-hidden flex-shrink-0 bg-white transition-all ${
                currentSrc === item.image
                  ? 'border-blue-600 shadow-sm scale-105'
                  : 'border-slate-200 opacity-70 hover:opacity-100'
              }`}
            >
              <img src={item.image} alt={item.alt_text || 'Thumbnail'} className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
