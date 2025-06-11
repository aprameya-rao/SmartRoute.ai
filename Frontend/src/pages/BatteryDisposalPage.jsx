import React from 'react';
import './BatteryDisposalPage.css';

function BatteryDisposalPage() {
  return (
    <div className="battery-disposal-page">
      <h1 className="text-3xl font-bold text-center mb-6">Battery Disposal and Recycling Information</h1>

      <section className="disposal-intro p-4 mb-6 bg-gray-100 rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">Why Proper Battery Disposal Matters</h2>
        <p className="text-gray-700 leading-relaxed">
          Proper disposal of <strong className="text-primary-green">all types of batteries</strong>, including household, automotive, and Electric Vehicle (EV) batteries, is crucial for environmental protection and resource recovery. Batteries contain valuable materials like lithium, cobalt, nickel, and lead, which can be recycled, as well as hazardous components that must be managed responsibly to prevent pollution and fire risks.
        </p>
      </section>

      <section className="general-disposal-resources p-4 mb-6 bg-white rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-4">General Battery Disposal Resources (Global & Specific)</h2>
        <p className="text-gray-700 leading-relaxed mb-4">
          When you're looking for information, always prioritize official government sites or reputable non-profit organizations for the most accurate and up-to-date guidelines on battery disposal in your specific region.
        </p>

        <h3 className="text-xl font-semibold mb-3">Official & Non-Profit Resources:</h3>
        <ul className="list-disc list-inside space-y-2 mb-6 text-gray-700">
          <li>
            <strong>U.S. Environmental Protection Agency (EPA):</strong> They offer comprehensive guides on disposing of various battery types, from household to lithium-ion. You'll find clear recommendations and links to recycling locations.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.epa.gov/recycle/used-household-batteries" target="_blank" rel="noopener noreferrer" className="hover:underline">Used Household Batteries</a></li>
              <li><a href="https://www.epa.gov/hw/lithium-ion-battery-recycling" target="_blank" rel="noopener noreferrer" className="hover:underline">Lithium-Ion Battery Recycling</a></li>
            </ul>
          </li>
          <li>
            <strong>Call2Recycle:</strong> This well-known non-profit runs battery and cellphone recycling programs. Their site is a great place to find drop-off spots across North America.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.call2recycle.org/" target="_blank" rel="noopener noreferrer" className="hover:underline">Call2Recycle Official Site</a></li>
            </ul>
          </li>
          <li>
            <strong>Earth911:</strong> This site boasts a huge directory for finding recycling centers for all sorts of materials, including batteries, throughout the U.S. and Canada. Plus, they have helpful articles on recycling best practices.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://earth911.com/" target="_blank" rel="noopener noreferrer" className="hover:underline">Earth911 Official Site (search for batteries)</a></li>
            </ul>
          </li>
          <li>
            <strong>Central Pollution Control Board (CPCB) - EPR Battery (India):</strong> If you're in India, this is the official portal for Extended Producer Responsibility (EPR) under the Battery Waste Management Rules, 2022.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://eprbattery.cpcb.gov.in/" target="_blank" rel="noopener noreferrer" className="hover:underline">CPCB EPR Battery Portal</a></li>
            </ul>
          </li>
        </ul>

        <h3 className="text-xl font-semibold mb-3">Informative Blogs & Industry Websites:</h3>
        <ul className="list-disc list-inside space-y-2 text-gray-700">
          <li>
            <strong>Waste Mission Blog:</strong> You'll find articles here on various waste management topics, including detailed info on proper battery disposal and why recycling is so important.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://wastemission.com/blog/how-to-dispose-of-batteries/" target="_blank" rel="noopener noreferrer" className="hover:underline">How to Dispose of Batteries: Best Practices</a></li>
            </ul>
          </li>
          <li>
            <strong>Battery Recycling & Solutions Blog:</strong> Get insights into battery recycling, eco-friendly practices, and new recycling technologies, with articles dedicated to different battery types.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.batteryrecyclingandsolutions.com/blog" target="_blank" rel="noopener noreferrer" className="hover:underline">Battery Recycling & Solutions Blog</a></li>
            </ul>
          </li>
          <li>
            <strong>BATX Energies Blog (India):</strong> This blog focuses on lithium-ion battery recycling, covering its benefits, challenges, and processes, especially relevant for the Indian context.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://batxenergies.com/blog/" target="_blank" rel="noopener noreferrer" className="hover:underline">Recycling Batteries - Blogs | BATX Energies</a></li>
            </ul>
          </li>
          <li>
            <strong>EcoFlow Blog (Lithium Battery Disposal):</strong> This specific blog post dives into safe, legal, and eco-friendly ways to dispose of lithium batteries, covering practical steps and environmental risks.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.ecoflow.com/us/blog/lithium-battery-disposal-safe-legal-ecofriendly" target="_blank" rel="noopener noreferrer" className="hover:underline">Lithium Battery Disposal: Safe, Legal, and Eco-Friendly Ways</a></li>
            </ul>
          </li>
          <li>
            <strong>evpedia Blog (EV Battery Disposal):</strong> Find resources here on responsible battery disposal practices, particularly for Electric Vehicle (EV) batteries, highlighting their environmental benefits.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.evpedia.co.in/ev-blog/environmental-and-social-benefits-of-lithium-ion-battery-recycling" target="_blank" rel="noopener noreferrer" className="hover:underline">Environmental and Social Benefits of Lithium-Ion Battery Recycling</a></li>
              <li><a href="https://www.evpedia.co.in/ev-blog/best-practices-for-responsible-battery-disposal" target="_blank" rel="noopener noreferrer" className="hover:underline">Empowering Sustainability: Best Practices for Responsible Battery Disposal</a></li>
            </ul>
          </li>
          <li>
            <strong>GreenSutra® (India):</strong> This site offers a Q&A format with information on how to properly dispose of batteries, including different types and where you can drop them off in India.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://greensutra.in/question/how-to-dispose-batteries-properly/" target="_blank" rel="noopener noreferrer" className="hover:underline">How to dispose batteries properly?</a></li>
            </ul>
          </li>
          <li>
            <strong>DENIOS Inc. (Battery Safety):</strong> While their main focus is safety, this resource provides crucial information on preparing batteries for disposal, especially lithium-ion ones, and highlights the risks of improper handling.
            <ul className="list-disc list-inside ml-5 mt-1 text-sm text-blue-600">
              <li><a href="https://www.denios-us.com/resources/denios-magazine/disposing-of-batteries-safely" target="_blank" rel="noopener noreferrer" className="hover:underline">Safely Disposing of Batteries: Your Guide to Environmental Responsibility</a></li>
            </ul>
          </li>
        </ul>
      </section>

      <section className="disposal-intro p-4 mb-6 bg-gray-100 rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">EV Battery Disposal Information</h2>
        <p className="text-gray-700 leading-relaxed">
          Proper disposal of Electric Vehicle (EV) batteries is crucial for environmental protection and resource recovery. EV batteries contain valuable materials like lithium, cobalt, and nickel, which can be recycled, and hazardous components that must be managed responsibly.
        </p>
      </section>

      <section className="regulations-india p-4 mb-6 bg-white rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">Regulatory Framework in India</h2>
        <p className="text-gray-700 leading-relaxed mb-3">
          In India, the disposal and recycling of batteries, including EV batteries, are primarily governed by the <strong className="text-primary-green">Battery Waste Management Rules, 2022</strong>. Here are some key aspects:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-700">
          <li><strong className="text-primary-green">Extended Producer Responsibility (EPR):</strong> Producers (manufacturers and importers) are responsible for collecting and recycling batteries, meeting specific collection targets.</li>
          <li><strong className="text-primary-green">Centralized Online Portal:</strong> The Central Pollution Control Board (CPCB) has developed an online portal for producers, recyclers, and refurbishers to register and report.</li>
          <li><strong className="text-primary-green">Recycling Targets:</strong> The rules mandate specific recycling efficiencies and targets for various battery types.</li>
          <li><strong className="text-primary-green">Prohibition of Landfilling:</strong> It's important to know that batteries are prohibited from being landfilled or incinerated.</li>
          <li><strong className="text-primary-green">Recent Amendments:</strong> The <strong className="text-primary-green">Battery Waste Management (Second Amendment) Rules 2024</strong> introduced provisions for using minimum recycled material in new batteries, actively promoting a circular economy.</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-4">
          For more detailed information, you can refer to the official documents from the Ministry of Environment, Forest and Climate Change (MoEFCC) and the Central Pollution Control Board (CPCB).
        </p>
      </section>

      <section className="how-to-dispose p-4 mb-6 bg-gray-100 rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">How to Safely Dispose of EV Batteries</h2>
        <p className="text-gray-700 leading-relaxed mb-3">
          <strong className="text-primary-green">Never dispose of EV batteries in regular waste bins.</strong> Always contact authorized channels:
        </p>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li><strong className="text-primary-green">Vehicle Manufacturer/Dealer:</strong> Your EV manufacturer or authorized service center is usually your first point of contact. They have established ways to handle battery return and recycling.</li>
          <li><strong className="text-primary-green">Authorized Recyclers:</strong> Look for companies specifically authorized by the CPCB for battery recycling. These facilities have the right setup to safely dismantle and process EV batteries.</li>
          <li><strong className="text-primary-green">Producer Responsibility Organizations (PROs):</strong> Some producers work with PROs to manage their EPR duties, which includes collecting used batteries.</li>
        </ol>
      </section>

      <section className="recycling-companies-india p-4 mb-6 bg-white rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">Key EV Battery Recycling Companies in India</h2>
        <p className="text-gray-700 leading-relaxed mb-3">
          Here are some of the prominent companies involved in EV battery recycling and materials recovery in India:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-700">
          <li><strong className="text-primary-green">Attero Recycling:</strong> One of India's largest e-waste and battery recycling companies, actively involved in lithium-ion battery recycling.</li>
          <li><strong className="text-primary-green">Tata Chemicals:</strong> They're involved in developing technologies for lithium-ion battery recycling.</li>
          <li><strong className="text-primary-green">Gravita India:</strong> While specializing in lead recycling, they're also expanding into lithium-ion battery recycling.</li>
          <li><strong className="text-primary-green">LOHUM:</strong> This company focuses on both repurposing and recycling lithium-ion batteries.</li>
          <li><strong className="text-primary-green">RecycleKaro:</strong> A growing player in battery waste management and recycling.</li>
          <li><strong className="text-primary-green">Exide Industries:</strong> A major battery manufacturer that's also exploring recycling solutions.</li>
        </ul>
      </section>

      <section className="second-life p-4 mb-6 bg-gray-100 rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">Second Life Applications</h2>
        <p className="text-gray-700 leading-relaxed mb-3">
          Before full recycling, EV batteries often get a "second life." Even after their capacity isn't optimal for vehicles anymore, they can still be very effective for:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-700">
          <li><strong className="text-primary-green">Stationary Energy Storage:</strong> Used in homes, businesses, or grid-scale applications to store renewable energy (like solar or wind) or provide backup power.</li>
          <li><strong className="text-primary-green">Telecommunications Towers:</strong> They can provide power backup for mobile towers.</li>
          <li><strong className="text-primary-green">E-Rickshaws and Low-Speed EVs:</strong> Sometimes, they're repurposed for less demanding electric vehicles.</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-4">
          This process extends the useful life of batteries, which helps reduce the demand for new materials and minimizes environmental impact.
        </p>
      </section>

      <section className="faqs p-4 mb-6 bg-white rounded-lg shadow-sm">
        <h2 className="text-2xl font-semibold mb-3">Frequently Asked Questions</h2>
        <dl className="text-gray-700">
          <dt className="font-semibold mt-3">What is the average lifespan of an EV battery?</dt>
          <dd className="ml-5">Most EV batteries are designed to last 8-10 years or 160,000-240,000 km, though their performance will gradually degrade over time.</dd>

          <dt className="font-semibold mt-3">Can I sell my old EV battery?</dt>
          <dd className="ml-5">It's always best to return it through authorized channels (like the manufacturer or a certified recycler) rather than selling it informally. This ensures proper and safe handling.</dd>

          <dt className="font-semibold mt-3">Are EV batteries environmentally friendly?</dt>
          <dd className="ml-5">While their manufacturing does have an impact, the overall environmental footprint of EV batteries throughout their full lifecycle, especially with proper recycling, is significantly lower than that of internal combustion engine vehicles. This is mainly due to zero tailpipe emissions.</dd>
        </dl>
      </section>
    </div>
  );
}

export default BatteryDisposalPage;